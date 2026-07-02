#!/usr/bin/env python3
"""CAB Audit — Static analysis of anchor structures against CAB type rules.

Usage:
    python cab-audit.py <anchor-path> [--level 5] [--type code] [--json] [--verbose]

Default level is 5, which includes module doc comparison.
"""

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


# ── Data Model ─────────────────────────────────────────────────────────────────


class AnchorType(Enum):
    SIMPLE = "simple"
    TOPIC = "topic"
    CODE = "code"
    PAPER = "paper"
    SKILL = "skill"


class Status(Enum):
    PASS = "pass"
    CONCERN = "concern"
    FAIL = "fail"
    SKIP = "skip"


@dataclass
class MethodInfo:
    name: str
    visibility: str = ""
    signature: str = ""

    def __eq__(self, other):
        return isinstance(other, MethodInfo) and self.name == other.name


@dataclass
class ClassInfo:
    name: str
    visibility: str = ""
    is_enum: bool = False
    fields: list[str] = field(default_factory=list)
    variants: list[str] = field(default_factory=list)  # enum variants
    methods: list[MethodInfo] = field(default_factory=list)

    def __eq__(self, other):
        return isinstance(other, ClassInfo) and self.name == other.name


@dataclass
class ModuleInfo:
    file_path: str
    doc_path: str = ""
    classes: list[ClassInfo] = field(default_factory=list)
    free_functions: list[MethodInfo] = field(default_factory=list)
    mtime: float = 0.0


@dataclass
class LintResult:
    rule_id: str
    level: int
    status: Status
    message: str
    file: str = ""


def _has_description(content: str) -> bool:
    """Check if content has a description via YAML frontmatter or legacy desc:: inline."""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            frontmatter = content[3:end]
            if re.search(r"^description:", frontmatter, re.MULTILINE):
                return True
    if "desc::" in content:
        return True
    return False


@dataclass
class Anchor:
    path: Path
    anchor_type: AnchorType
    name: str = ""
    folder_name: str = ""
    marker_file: Optional[Path] = None
    anchor_page: Optional[Path] = None
    code_path: Optional[Path] = None
    docs_folder: Optional[Path] = None
    dev_folder: Optional[Path] = None

    def __post_init__(self):
        self.folder_name = self.path.name
        self._detect()

    def _detect(self):
        # Marker file
        marker = self.path / f"{self.folder_name}.md"
        if marker.exists():
            self.marker_file = marker

        # Code path (symlink or inline .git)
        code = self.path / "Code"
        if code.is_symlink() and code.resolve().exists():
            self.code_path = code.resolve()
        elif (self.path / ".git").exists():
            self.code_path = self.path

        # Find anchor page (has description: in frontmatter, desc:: inline, or dispatch table)
        for f in self.path.glob("*.md"):
            if f.name == f"{self.folder_name}.md" or f.name == "CLAUDE.md":
                continue
            try:
                content = f.read_text(errors="replace")[:2000]
                if _has_description(content) or "-[[" in content:
                    self.anchor_page = f
                    self.name = f.stem
                    break
            except Exception:
                continue
        if not self.name:
            self.name = self.folder_name

        # Docs and Dev folders
        for d in self.path.iterdir():
            if d.is_dir() and d.name.endswith("Docs"):
                self.docs_folder = d
                for sub in d.iterdir():
                    if sub.is_dir() and sub.name.endswith("Dev"):
                        self.dev_folder = sub
                break


# ── Type Detection ─────────────────────────────────────────────────────────────


def detect_type(path: Path) -> AnchorType:
    if (path / "SKILL.md").exists():
        return AnchorType.SKILL
    if (path / "Code").is_symlink() or (path / ".git").exists():
        return AnchorType.CODE
    for f in path.glob("*.md"):
        try:
            content = f.read_text(errors="replace")[:3000]
            if "| Version" in content and "(original)" in content:
                return AnchorType.PAPER
        except Exception:
            continue
    child_anchors = sum(1 for d in path.iterdir()
                        if d.is_dir() and not d.name.startswith(".")
                        and (d / f"{d.name}.md").exists())
    if child_anchors >= 2:
        return AnchorType.TOPIC
    return AnchorType.SIMPLE


# ── Phase 1: Scanner ──────────────────────────────────────────────────────────


SOURCE_EXTENSIONS = {".rs", ".py", ".swift", ".js", ".ts"}

# Languages supported by tree-sitter-analyzer
TSA_LANGUAGES = {".rs": "rust", ".py": "python", ".js": "javascript", ".ts": "typescript"}

# Languages we parse directly with tree-sitter
DIRECT_LANGUAGES = {".swift"}


def parse_swift_file(file_path: Path) -> dict:
    """Parse a Swift file using tree-sitter directly. Returns structure dict."""
    try:
        import tree_sitter_swift as tsswift
        from tree_sitter import Language, Parser
    except ImportError:
        return {}

    swift_lang = Language(tsswift.language())
    parser = Parser(swift_lang)

    code = file_path.read_bytes()
    tree = parser.parse(code)
    root = tree.root_node

    classes = []
    methods = []
    fields = []
    imports = []

    def get_name(node):
        name_node = node.child_by_field_name("name")
        return name_node.text.decode() if name_node else "?"

    def get_visibility(node):
        for child in node.children:
            if child.type == "modifiers":
                text = child.text.decode()
                if "public" in text:
                    return "pub"
                if "private" in text:
                    return "private"
                if "internal" in text:
                    return "internal"
                if "fileprivate" in text:
                    return "fileprivate"
        return "internal"  # Swift default

    def walk(node):
        if node.type in ("class_declaration", "struct_declaration",
                         "enum_declaration", "protocol_declaration"):
            name = get_name(node)
            vis = get_visibility(node)
            classes.append({
                "name": name,
                "visibility": vis,
                "line_range": [node.start_point[0] + 1, node.end_point[0] + 1],
            })
            # Find properties and methods inside the body
            for child in node.children:
                if child.type in ("class_body", "struct_body", "enum_body",
                                  "enum_class_body", "protocol_body"):
                    for member in child.children:
                        if member.type == "property_declaration":
                            pname = get_name(member)
                            fields.append({
                                "name": pname,
                                "type": "",
                                "line_range": [member.start_point[0] + 1,
                                               member.end_point[0] + 1],
                            })
                        elif member.type == "function_declaration":
                            mname = get_name(member)
                            mvis = get_visibility(member)
                            methods.append({
                                "name": mname,
                                "visibility": mvis,
                                "line_range": [member.start_point[0] + 1,
                                               member.end_point[0] + 1],
                            })

        elif node.type == "import_declaration":
            imports.append({
                "name": node.text.decode(),
                "is_static": False,
                "is_wildcard": False,
                "statement": node.text.decode(),
                "line_range": [node.start_point[0] + 1, node.end_point[0] + 1],
            })

        # Recurse for top-level extensions
        elif node.type == "extension_declaration":
            # Extensions add methods to existing types
            name = get_name(node)
            for child in node.children:
                if child.type in ("class_body", "enum_class_body", "extension_body"):
                    for member in child.children:
                        if member.type == "function_declaration":
                            mname = get_name(member)
                            mvis = get_visibility(member)
                            methods.append({
                                "name": mname,
                                "visibility": mvis,
                                "line_range": [member.start_point[0] + 1,
                                               member.end_point[0] + 1],
                            })

        for child in node.children:
            if child.type not in ("class_body", "struct_body", "enum_body",
                                  "enum_class_body", "protocol_body", "extension_body"):
                walk(child)

    walk(root)

    line_count = code.count(b"\n") + 1
    return {
        "file_path": str(file_path),
        "language": "swift",
        "package": None,
        "classes": classes,
        "methods": methods,
        "fields": fields,
        "imports": imports,
        "statistics": {
            "class_count": len(classes),
            "method_count": len(methods),
            "field_count": len(fields),
            "import_count": len(imports),
            "total_lines": line_count,
        },
    }


def scan_source_tree(repo_path: Path, cache_dir: Path, verbose: bool = False) -> int:
    """Scan source files and update cache. Returns number of files parsed."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    parsed = 0

    for root, dirs, files in os.walk(repo_path):
        # Skip hidden dirs, build dirs, test dirs
        dirs[:] = [d for d in dirs if not d.startswith(".")
                   and d not in {"build", "DerivedData", "target", "__pycache__",
                                 "node_modules", ".build", "checkouts", "tests",
                                 "test", "spec", "fixtures"}]
        for fname in files:
            ext = Path(fname).suffix
            if ext not in TSA_LANGUAGES and ext not in DIRECT_LANGUAGES:
                continue

            src_file = Path(root) / fname
            rel_path = src_file.relative_to(repo_path)
            cache_file = cache_dir / f"{rel_path}.json"

            # Check mtime
            if cache_file.exists():
                src_mtime = src_file.stat().st_mtime
                cache_mtime = cache_file.stat().st_mtime
                if cache_mtime >= src_mtime:
                    if verbose:
                        print(f"  cache current: {rel_path}")
                    continue

            if verbose:
                print(f"  parsing: {rel_path}")

            try:
                # Swift: use direct tree-sitter parser
                if ext in DIRECT_LANGUAGES:
                    if ext == ".swift":
                        data = parse_swift_file(src_file)
                        if not data:
                            if verbose:
                                print(f"  WARN: Swift parser not available for {rel_path}")
                            continue
                        cache_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(cache_file, "w") as f:
                            json.dump(data, f, indent=2)
                        parsed += 1
                    continue

                # Rust/Python/JS/TS: use tree-sitter-analyzer
                result = subprocess.run(
                    ["tree-sitter-analyzer", str(src_file),
                     "--structure", "--output-format=json"],
                    capture_output=True, text=True, timeout=30
                )
                if result.returncode != 0:
                    if verbose:
                        print(f"  WARN: parser failed for {rel_path}")
                    continue

                # Extract JSON from output (may have prefix text)
                output = result.stdout
                json_start = output.find("{")
                if json_start < 0:
                    continue
                data = json.loads(output[json_start:])

                # Write cache
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                with open(cache_file, "w") as f:
                    json.dump(data, f, indent=2)
                parsed += 1

            except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
                if verbose:
                    print(f"  WARN: {rel_path}: {e}")

    return parsed


# ── Phase 2: Loaders ──────────────────────────────────────────────────────────


def load_source_modules(cache_dir: Path) -> list[ModuleInfo]:
    """Load cached source analysis into ModuleInfo list."""
    modules = []
    if not cache_dir.exists():
        return modules

    for cache_file in sorted(cache_dir.rglob("*.json")):
        try:
            with open(cache_file) as f:
                data = json.load(f)
        except Exception:
            continue

        rel_path = str(cache_file.relative_to(cache_dir))
        if rel_path.endswith(".json"):
            rel_path = rel_path[:-5]  # strip .json to get original path

        classes_raw = data.get("classes", [])
        methods_raw = data.get("methods", [])
        fields_raw = data.get("fields", [])

        # Associate methods and fields with classes by line range
        class_infos = []
        claimed_methods = set()
        claimed_fields = set()

        for c in classes_raw:
            cstart, cend = c.get("line_range", [0, 0])
            cname = c.get("name", "")

            # Find fields within this class
            cls_fields = []
            for i, fld in enumerate(fields_raw):
                fstart = fld.get("line_range", [0, 0])[0]
                if cstart <= fstart <= cend:
                    cls_fields.append(fld.get("name", ""))
                    claimed_fields.add(i)

            # Find methods in impl blocks for this class
            # Heuristic: methods after the struct def, before the next struct
            cls_methods = []
            # For Rust: look for methods in impl blocks (after struct, within ~5000 lines)
            next_class_start = float("inf")
            for c2 in classes_raw:
                c2start = c2.get("line_range", [0, 0])[0]
                if c2start > cend:
                    next_class_start = min(next_class_start, c2start)

            for i, m in enumerate(methods_raw):
                mstart = m.get("line_range", [0, 0])[0]
                # Method is inside the class definition
                if cstart <= mstart <= cend:
                    cls_methods.append(MethodInfo(
                        name=m.get("name", ""),
                        visibility=m.get("visibility", ""),
                    ))
                    claimed_methods.add(i)

            class_infos.append(ClassInfo(
                name=cname,
                visibility=c.get("visibility", ""),
                fields=cls_fields,
                methods=cls_methods,
            ))

        # Unclaimed methods = free functions or impl-block methods
        # For impl-block methods, try to match by name patterns or just list them
        free_fns = []
        unclaimed = [(i, m) for i, m in enumerate(methods_raw) if i not in claimed_methods]

        # Second pass: try to associate unclaimed methods with classes
        # by checking if they appear in an impl block (Rust-specific heuristic)
        for i, m in unclaimed:
            mstart = m.get("line_range", [0, 0])[0]
            assigned = False
            for ci in class_infos:
                # Find the class's line range
                for c in classes_raw:
                    if c["name"] == ci.name:
                        cend = c["line_range"][1]
                        # Methods in impl blocks typically come after the struct
                        # and before the next struct
                        next_start = float("inf")
                        for c2 in classes_raw:
                            c2s = c2["line_range"][0]
                            if c2s > cend:
                                next_start = min(next_start, c2s)
                        if cend < mstart < next_start:
                            ci.methods.append(MethodInfo(
                                name=m.get("name", ""),
                                visibility=m.get("visibility", ""),
                            ))
                            assigned = True
                            break
                if assigned:
                    break
            if not assigned:
                free_fns.append(MethodInfo(
                    name=m.get("name", ""),
                    visibility=m.get("visibility", ""),
                ))

        mod = ModuleInfo(
            file_path=rel_path,
            classes=class_infos,
            free_functions=free_fns,
            mtime=cache_file.stat().st_mtime,
        )
        modules.append(mod)

    return modules


def load_doc_modules(dev_folder: Path, name_prefix: str) -> list[ModuleInfo]:
    """Load module docs from Dev folder into ModuleInfo list."""
    modules = []
    if not dev_folder or not dev_folder.exists():
        return modules

    for md_file in sorted(dev_folder.rglob("*.md")):
        # Skip dispatch pages (Dev.md, etc.)
        fname = md_file.name
        if fname.endswith("Dev.md") or fname.endswith("Docs.md"):
            continue
        if fname.endswith("Files.md") or fname.endswith("Architecture.md"):
            continue

        try:
            content = md_file.read_text(errors="replace")
        except Exception:
            continue

        # Parse the module doc for classes and methods
        classes = []
        current_class = None
        in_methods_section = False

        for line in content.split("\n"):
            # Detect CLASSES table entries: | [[#ClassName]] | description |
            m = re.match(r'\|\s*\[\[#(\w+)\]\]\s*\|', line)
            if m:
                # This is a CLASSES table entry
                continue

            # Detect per-class table header: | CLASS NAME ([[#^N|details]]) |
            m = re.match(r'\|\s*([A-Z][A-Z\s]+?)\s*\(\[\[', line)
            if m:
                class_name_upper = m.group(1).strip()
                # Convert ALL CAPS WITH SPACES back to PascalCase
                parts = class_name_upper.split()
                pascal = "".join(p.capitalize() for p in parts)
                # Will detect enum vs struct from content (see below)
                current_class = ClassInfo(name=pascal)
                classes.append(current_class)
                in_methods_section = False
                continue

            # Also detect: | CLASS NAME | Type | Desc | (without details link)
            # Exclude common table section headers that aren't class names
            _TABLE_HEADERS = {"CLASSES", "METHODS", "PROPERTIES", "FIELDS", "TYPES",
                              "FUNCTIONS", "STRUCTS", "NAME", "CLASS", "METHOD",
                              "FUNCTION", "FIELD", "PROPERTY", "CONSTANT", "VARIANT",
                              "STEP", "FILES", "ACTIONS", "DESCRIPTION", "RETURNS",
                              "TYPE", "MODULE", "SECTION", "DOCUMENT", "USAGE"}
            m = re.match(r'\|\s*([A-Z][A-Z\s]{2,}?)\s*\|', line)
            if m and "---" not in line and "**Methods**" not in line:
                candidate = m.group(1).strip()
                if (candidate and candidate not in _TABLE_HEADERS
                        and not candidate.startswith("--")):
                    parts = candidate.split()
                    pascal = "".join(p.capitalize() for p in parts)
                    # Only if it looks like a class header (not a regular row)
                    if all(c.isupper() or c.isspace() for c in candidate):
                        current_class = ClassInfo(name=pascal)
                        classes.append(current_class)
                        in_methods_section = False
                        continue

            if current_class:
                # Detect **Methods** separator
                if "**Methods**" in line:
                    in_methods_section = True
                    continue

                # Detect field or enum variant
                if not in_methods_section:
                    # Check for enum variant patterns:
                    # 1. Two-column: | VariantName | Desc |
                    # 2. Three-column with "variant" type: | `VariantName` | variant | Desc |
                    # 3. PascalCase backtick name: | `PascalCaseName` | ... |
                    m = re.match(r'\|\s*`?(\w+)`?\s*\|([^|]*)\|', line)
                    if m and "---" not in line:
                        name = m.group(1)
                        type_col = m.group(2).strip().lower()
                        is_variant = (
                            type_col == "variant"
                            or (name[0].isupper() and not name.startswith("_")
                                and "_" not in name and len(name) > 1)
                        )
                        if is_variant:
                            current_class.is_enum = True
                            current_class.variants.append(name)
                        else:
                            current_class.fields.append(name)
                        continue

                # Detect method: | [[#sig|name]] | or | name | (in methods section)
                if in_methods_section:
                    # Wiki-link method: [[#signature|display_name]]
                    m = re.match(r'\|\s*\[\[#[^|]*\|(\w+)', line)
                    if m:
                        current_class.methods.append(MethodInfo(name=m.group(1)))
                        continue
                    # Plain method name
                    m = re.match(r'\|\s*(\w+)\s*\|', line)
                    if m and "---" not in line:
                        name = m.group(1)
                        if name and name[0].islower():
                            current_class.methods.append(MethodInfo(name=name))
                            continue

        if classes:
            modules.append(ModuleInfo(
                file_path="",
                doc_path=str(md_file),
                classes=classes,
                mtime=md_file.stat().st_mtime,
            ))

    return modules


# ── Phase 3: Comparator ──────────────────────────────────────────────────────


def compare_modules(source_modules: list[ModuleInfo],
                    doc_modules: list[ModuleInfo],
                    include_private: bool = False,
                    pub_only: bool = False,
                    lint_level: int = 5) -> list[LintResult]:
    """Compare source modules against doc modules."""
    results = []

    # Build lookup by class name (case-insensitive) → source module
    source_classes: dict[str, tuple[ModuleInfo, ClassInfo]] = {}
    for mod in source_modules:
        for cls in mod.classes:
            source_classes[cls.name.lower()] = (mod, cls)

    # Build lookup by class name (case-insensitive) → doc module
    doc_classes: dict[str, tuple[ModuleInfo, ClassInfo]] = {}
    for mod in doc_modules:
        for cls in mod.classes:
            doc_classes[cls.name.lower()] = (mod, cls)

    def _skip_visibility(vis: str) -> bool:
        """Return True if this visibility should be skipped."""
        if include_private:
            return False
        if pub_only:
            return vis != "pub"
        return vis == "private"

    # Classes in source but not in docs
    for key in sorted(source_classes.keys()):
        if key not in doc_classes:
            mod, cls = source_classes[key]
            if _skip_visibility(cls.visibility):
                continue
            results.append(LintResult(
                rule_id="class-undocumented",
                level=5,
                status=Status.CONCERN,
                message=f"Class '{cls.name}' in source ({mod.file_path}) has no module doc",
                file=mod.file_path,
            ))

    # Classes in docs but not in source
    for key in sorted(doc_classes.keys()):
        if key not in source_classes:
            mod, cls = doc_classes[key]
            results.append(LintResult(
                rule_id="class-stale-doc",
                level=5,
                status=Status.CONCERN,
                message=f"Class '{cls.name}' in doc ({mod.doc_path}) not found in source — stale?",
                file=mod.doc_path,
            ))

    # Classes in both — compare methods and fields
    for key in sorted(set(source_classes.keys()) & set(doc_classes.keys())):
        src_mod, src_cls = source_classes[key]
        doc_mod, doc_cls = doc_classes[key]

        # Methods in source but not in doc
        src_method_names = {m.name for m in src_cls.methods}
        doc_method_names = {m.name for m in doc_cls.methods}

        for mname in sorted(src_method_names - doc_method_names):
            src_method = next((m for m in src_cls.methods if m.name == mname), None)
            if src_method and _skip_visibility(src_method.visibility):
                continue
            results.append(LintResult(
                rule_id="method-undocumented",
                level=5,
                status=Status.CONCERN,
                message=f"Method '{src_cls.name}.{mname}' in source but not in module doc",
                file=src_mod.file_path,
            ))

        # Methods in doc but not in source
        for mname in sorted(doc_method_names - src_method_names):
            results.append(LintResult(
                rule_id="method-stale-doc",
                level=5,
                status=Status.CONCERN,
                message=f"Method '{src_cls.name}.{mname}' in doc but not in source — removed?",
                file=doc_mod.doc_path,
            ))

        # Field/variant comparison
        # If doc marks this as an enum, compare variants not fields
        if (doc_cls.is_enum and doc_cls.variants) or (src_cls.is_enum and src_cls.variants):
            # Enum: source "fields" are really variant associated data,
            # doc "variants" are the variant names. These are different things.
            # Don't compare them — the doc has the right data (variant names).
            # Source parser doesn't give us variant names for Rust yet.
            pass
        else:
            # Struct: compare fields normally
            if len(src_cls.fields) != len(doc_cls.fields):
                results.append(LintResult(
                    rule_id="field-count-mismatch",
                    level=5,
                    status=Status.CONCERN,
                    message=f"Class '{src_cls.name}': {len(src_cls.fields)} fields in source, {len(doc_cls.fields)} in doc",
                    file=src_mod.file_path,
                ))

            src_field_set = set(src_cls.fields)
            doc_field_set = set(doc_cls.fields)
            for fname in sorted(src_field_set - doc_field_set):
                results.append(LintResult(
                    rule_id="field-undocumented",
                    level=5,
                    status=Status.CONCERN,
                    message=f"Field '{src_cls.name}.{fname}' in source but not in doc",
                    file=src_mod.file_path,
                ))
            for fname in sorted(doc_field_set - src_field_set):
                results.append(LintResult(
                    rule_id="field-stale-doc",
                    level=5,
                    status=Status.CONCERN,
                    message=f"Field '{src_cls.name}.{fname}' in doc but not in source — removed?",
                    file=doc_mod.doc_path,
                ))

    return results


# ── Structural Lint Rules (Levels 1-4) ────────────────────────────────────────


def lint_structure(anchor: Anchor, level: int) -> list[LintResult]:
    """Run structural lint rules up to the given level."""
    results = []

    # Level 1: Bare Bones
    if level >= 1:
        if anchor.marker_file and anchor.marker_file.exists():
            results.append(LintResult("marker-file", 1, Status.PASS, f"Marker file: {anchor.marker_file.name}"))
        else:
            results.append(LintResult("marker-file", 1, Status.FAIL, f"Missing: {anchor.folder_name}.md"))

        if anchor.anchor_page and anchor.anchor_page.exists():
            results.append(LintResult("anchor-page", 1, Status.PASS, f"Anchor page: {anchor.anchor_page.name}"))
        else:
            results.append(LintResult("anchor-page", 1, Status.FAIL, "No anchor page found"))

    # Level 2: Core (type-specific)
    if level >= 2 and anchor.anchor_type == AnchorType.CODE:
        claude = anchor.path / "CLAUDE.md"
        if claude.exists():
            results.append(LintResult("code-has-claude", 2, Status.PASS, "CLAUDE.md present"))
        else:
            results.append(LintResult("code-has-claude", 2, Status.CONCERN, "No CLAUDE.md"))

        if anchor.code_path:
            results.append(LintResult("code-symlink-valid", 2, Status.PASS, f"Code: {anchor.code_path}"))
            readme = anchor.code_path / "README.md"
            if readme.exists():
                results.append(LintResult("code-has-readme", 2, Status.PASS, "README.md in repo"))
            else:
                results.append(LintResult("code-has-readme", 2, Status.CONCERN, "No README.md in repo"))
        else:
            results.append(LintResult("code-symlink-valid", 2, Status.FAIL, "No Code symlink or .git"))

    if level >= 2 and anchor.anchor_type == AnchorType.SKILL:
        skill = anchor.path / "SKILL.md"
        if skill.exists():
            results.append(LintResult("skill-has-skillmd", 2, Status.PASS, "SKILL.md present"))
        else:
            results.append(LintResult("skill-has-skillmd", 2, Status.FAIL, "Missing SKILL.md"))

    # Level 3: Structure
    if level >= 3 and anchor.anchor_type in (AnchorType.CODE, AnchorType.TOPIC):
        if anchor.docs_folder and anchor.docs_folder.exists():
            results.append(LintResult("docs-folder", 3, Status.PASS, f"Docs: {anchor.docs_folder.name}"))
            dispatch = anchor.docs_folder / f"{anchor.docs_folder.name}.md"
            if dispatch.exists():
                results.append(LintResult("docs-dispatch", 3, Status.PASS, f"Docs dispatch: {dispatch.name}"))
            else:
                results.append(LintResult("docs-dispatch", 3, Status.CONCERN, f"Missing: {dispatch.name}"))
        else:
            results.append(LintResult("docs-folder", 3, Status.CONCERN, "No Docs folder"))

    # Level 3: Files skeleton (Code anchors)
    if level >= 3 and anchor.anchor_type == AnchorType.CODE and anchor.dev_folder:
        # Check Files.md exists
        files_md = None
        # Search Docs folder recursively for Files.md (may be in Dev/)
        for f in anchor.docs_folder.rglob("*Files.md") if anchor.docs_folder else []:
            files_md = f
            break
        if files_md:
            results.append(LintResult("files-exists", 3, Status.PASS, f"Files: {files_md.name}"))
        else:
            results.append(LintResult("files-exists", 3, Status.CONCERN,
                                      f"No Files.md in Docs folder"))

        # Check Dev dispatch exists and links to module docs
        dev_dispatch = anchor.dev_folder / f"{anchor.dev_folder.name}.md"
        if dev_dispatch.exists():
            try:
                dev_content = dev_dispatch.read_text(errors="replace")
            except Exception:
                dev_content = ""

            # Find all module doc files in Dev folder (excluding dispatch pages)
            module_docs = []
            for md_file in sorted(anchor.dev_folder.rglob("*.md")):
                fname = md_file.name
                if (fname.endswith("Dev.md") or fname.endswith("Docs.md")
                        or fname.endswith("Files.md") or fname.endswith("Architecture.md")):
                    continue
                module_docs.append(md_file)

            # Check each module doc is linked from Dev dispatch
            unlinked = []
            for md_file in module_docs:
                # Check if the file stem appears as a wiki-link in dev dispatch
                stem = md_file.stem
                if f"[[{stem}" not in dev_content and f"|{stem}" not in dev_content:
                    unlinked.append(stem)

            if unlinked:
                for name in unlinked[:10]:  # limit output
                    results.append(LintResult("module-not-in-dev", 3, Status.CONCERN,
                                              f"Module doc '{name}' not linked from Dev dispatch"))
                if len(unlinked) > 10:
                    results.append(LintResult("module-not-in-dev", 3, Status.CONCERN,
                                              f"... and {len(unlinked) - 10} more unlinked module docs"))
            elif module_docs:
                results.append(LintResult("module-docs-linked", 3, Status.PASS,
                                          f"All {len(module_docs)} module docs linked from Dev dispatch"))

            # Check Files.md links to module docs
            if files_md:
                try:
                    files_content = files_md.read_text(errors="replace")
                except Exception:
                    files_content = ""
                files_unlinked = []
                for md_file in module_docs:
                    stem = md_file.stem
                    if f"[[{stem}" not in files_content and f"|{stem}" not in files_content:
                        files_unlinked.append(stem)
                if files_unlinked:
                    for name in files_unlinked[:10]:
                        results.append(LintResult("module-not-in-files", 3, Status.CONCERN,
                                                  f"Module doc '{name}' not linked from Files.md"))
                    if len(files_unlinked) > 10:
                        results.append(LintResult("module-not-in-files", 3, Status.CONCERN,
                                                  f"... and {len(files_unlinked) - 10} more"))
                elif module_docs:
                    results.append(LintResult("modules-in-files", 3, Status.PASS,
                                              f"All {len(module_docs)} module docs linked from Files.md"))

        # Check source files have corresponding module docs
        if anchor.code_path:
            source_files = set()
            for root_dir, dirs, files in os.walk(anchor.code_path):
                dirs[:] = [d for d in dirs if not d.startswith(".")
                           and d not in {"build", "DerivedData", "target", "__pycache__",
                                         "node_modules", ".build", "checkouts", "tests",
                                         "test", "spec", "fixtures"}]
                for fname in files:
                    ext = Path(fname).suffix
                    if ext in {".rs", ".py", ".swift", ".js", ".ts"}:
                        source_files.add(Path(root_dir) / fname)

            # For each source file, check if ANY class from it appears in module docs
            # Simple heuristic: check if source filename stem appears in any module doc name
            doc_stems = {md.stem.lower() for md in module_docs}
            undocumented_sources = []
            for src in sorted(source_files):
                src_stem = src.stem.lower()
                # Check if any module doc contains this source's classes
                # Simple: does any doc name contain the source name?
                has_doc = any(src_stem in ds or ds in src_stem for ds in doc_stems)
                if not has_doc and src_stem not in {"mod", "lib", "main", "__init__",
                                                     "prelude", "build", "package"}:
                    rel = src.relative_to(anchor.code_path)
                    undocumented_sources.append(str(rel))

            # Check source FOLDERS have folder docs
            source_folders = set()
            for src in source_files:
                parent = src.parent
                if parent != anchor.code_path:  # skip repo root
                    source_folders.add(parent)

            undocumented_folders = []
            for folder in sorted(source_folders):
                # Count source files in this folder (not subfolders)
                files_in_folder = sum(1 for f in source_files if f.parent == folder)
                if files_in_folder < 2:
                    continue  # single-file folders don't need folder docs
                folder_name = folder.name.lower()
                has_doc = any(folder_name in ds for ds in doc_stems)
                if not has_doc:
                    rel = folder.relative_to(anchor.code_path)
                    undocumented_folders.append(str(rel))

            if undocumented_folders:
                for name in undocumented_folders[:10]:
                    results.append(LintResult("folder-no-doc", 3, Status.CONCERN,
                                              f"Source folder '{name}' has no folder doc — folder docs are almost always wanted; think carefully before excepting",
                                              file=name))
                if len(undocumented_folders) > 10:
                    results.append(LintResult("folder-no-doc", 3, Status.CONCERN,
                                              f"... and {len(undocumented_folders) - 10} more"))

            if undocumented_sources:
                for name in undocumented_sources[:10]:
                    results.append(LintResult("source-no-module-doc", 3, Status.CONCERN,
                                              f"Source '{name}' has no corresponding module doc"))
                if len(undocumented_sources) > 10:
                    results.append(LintResult("source-no-module-doc", 3, Status.CONCERN,
                                              f"... and {len(undocumented_sources) - 10} more"))
            elif source_files:
                results.append(LintResult("source-coverage", 3, Status.PASS,
                                          f"All {len(source_files)} source files have module docs"))

    # Level 4: Markdown format checks
    if level >= 4 and anchor.anchor_type in (AnchorType.CODE, AnchorType.TOPIC, AnchorType.SKILL):
        md_format_issues = 0
        docs_root = anchor.docs_folder or anchor.path
        for md_file in docs_root.rglob("*.md"):
            try:
                content = md_file.read_text(errors="replace")
            except Exception:
                continue
            for line_num, line in enumerate(content.split("\n"), 1):
                # Only check lines that are table rows
                if not line.startswith("|"):
                    continue
                # Look for unescaped | inside [[ ]] wiki-links
                # Pattern: [[ followed by content with unescaped | before ]]
                import re as _re
                matches = _re.findall(r'\[\[[^\]]*(?<!\\)\|[^\]]*\]\]', line)
                for match in matches:
                    # This wiki-link has an unescaped | inside a table row
                    md_format_issues += 1
                    if md_format_issues <= 5:
                        rel = md_file.relative_to(anchor.path) if md_file.is_relative_to(anchor.path) else md_file.name
                        results.append(LintResult(
                            "md-unescaped-pipe", 4, Status.CONCERN,
                            f"Unescaped | in wiki-link inside table: {rel}:{line_num}",
                            file=str(rel),
                        ))
        if md_format_issues > 5:
            results.append(LintResult(
                "md-unescaped-pipe", 4, Status.CONCERN,
                f"... and {md_format_issues - 5} more unescaped | in wiki-links",
            ))
        elif md_format_issues == 0:
            results.append(LintResult("md-format", 4, Status.PASS, "No markdown format issues"))

    # Level 4: Content
    if level >= 4:
        page = anchor.anchor_page or anchor.marker_file
        if page and page.exists():
            try:
                content = page.read_text(errors="replace")[:3000]
                if _has_description(content):
                    results.append(LintResult("has-desc", 4, Status.PASS, "description found"))
                else:
                    results.append(LintResult("has-desc", 4, Status.CONCERN, "No description: in frontmatter (or legacy desc::)"))
                if ":>>" in content:
                    results.append(LintResult("has-breadcrumb", 4, Status.PASS, "Breadcrumb found"))
                else:
                    results.append(LintResult("has-breadcrumb", 4, Status.CONCERN, "No breadcrumb"))
                if "-[[" in content and "]]-" in content:
                    results.append(LintResult("dispatch-table", 4, Status.PASS, "Dispatch table found"))
                else:
                    results.append(LintResult("dispatch-table", 4, Status.CONCERN, "No dispatch table"))
            except Exception:
                pass

    return results


# ── Output ─────────────────────────────────────────────────────────────────────


def gate(results: list[LintResult]) -> str:
    statuses = [r.status for r in results if r.status != Status.SKIP]
    if any(s == Status.FAIL for s in statuses):
        return "FAIL"
    if any(s == Status.CONCERN for s in statuses):
        return "CONCERNS"
    return "PASS"


def report_markdown(anchor: Anchor, results: list[LintResult], level: int) -> str:
    lines = [
        f"## CAB Audit: {anchor.folder_name}",
        f"Type: {anchor.anchor_type.value.title()} Anchor | Level: {level}",
        "",
    ]

    passed = [r for r in results if r.status == Status.PASS]
    concerns = [r for r in results if r.status == Status.CONCERN]
    failed = [r for r in results if r.status == Status.FAIL]

    if failed:
        lines.append(f"### FAIL ({len(failed)})")
        for r in failed:
            lines.append(f"  ✗ {r.rule_id} — {r.message}")
        lines.append("")

    if concerns:
        lines.append(f"### CONCERNS ({len(concerns)})")
        for r in concerns:
            lines.append(f"  ⚠ {r.rule_id} — {r.message}")
        lines.append("")

    if passed:
        lines.append(f"### PASS ({len(passed)})")
        for r in passed:
            lines.append(f"  ✓ {r.rule_id} — {r.message}")
        lines.append("")

    lines.append(f"**Result: {gate(results)}**")
    return "\n".join(lines)


def report_json(anchor: Anchor, results: list[LintResult], level: int) -> str:
    return json.dumps({
        "anchor": anchor.folder_name,
        "type": anchor.anchor_type.value,
        "level": level,
        "gate": gate(results),
        "results": [
            {"id": r.rule_id, "level": r.level, "status": r.status.value,
             "message": r.message, "file": r.file}
            for r in results
        ],
    }, indent=2)


# ── Exceptions ─────────────────────────────────────────────────────────────────


@dataclass
class Exception_:
    module: str   # glob pattern for source path
    target: str   # class, method, or field name (empty = whole module)
    rule: str     # rule ID
    reason: str


def load_exceptions_from_file(exc_file: Path) -> list[Exception_]:
    """Load exceptions from a markdown table file."""
    if not exc_file.exists():
        return []

    exceptions = []
    try:
        content = exc_file.read_text(errors="replace")
        for line in content.split("\n"):
            # Parse table rows: | Module | Target | Rule | Reason |
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|")]
            # Skip header, separator, empty
            if len(parts) < 5:
                continue
            module, target, rule, reason = parts[1], parts[2], parts[3], parts[4]
            if module in ("Module", "---") or "---" in module:
                continue
            if module == "":
                module = "*"  # empty module = match any
            # Reject blanket suppressions: * with no target for content rules
            if module == "*" and target == "" and rule in (
                "field-undocumented", "field-stale-doc", "field-count-mismatch",
                "method-undocumented", "method-stale-doc",
                "class-undocumented", "class-stale-doc",
            ):
                print(f"WARNING: Blanket exception rejected: * | | {rule} — must specify Module or Target", file=sys.stderr)
                continue
            exceptions.append(Exception_(
                module=module, target=target, rule=rule, reason=reason,
            ))
    except Exception:
        pass

    return exceptions


def load_exceptions(anchor_path: Path) -> list[Exception_]:
    """Load project exceptions from .skl/lint/exceptions.md"""
    return load_exceptions_from_file(anchor_path / ".skl" / "lint" / "exceptions.md")


def is_excepted(result: LintResult, exceptions: list[Exception_]) -> bool:
    """Check if a lint result is suppressed by an exception."""
    for exc in exceptions:
        if exc.rule != result.rule_id:
            continue
        # Match module path (glob)
        if exc.module:
            if not fnmatch.fnmatch(result.file, exc.module) and result.file != exc.module:
                # Also try matching just the filename
                if not fnmatch.fnmatch(os.path.basename(result.file), exc.module):
                    continue
        # Match target (if specified)
        if exc.target:
            if exc.target not in result.message:
                continue
        return True
    return False


def filter_exceptions(results: list[LintResult],
                      exceptions: list[Exception_]) -> tuple[list[LintResult], int]:
    """Filter out excepted results. Returns (filtered, suppressed_count)."""
    if not exceptions:
        return results, 0
    filtered = []
    suppressed = 0
    for r in results:
        if is_excepted(r, exceptions):
            suppressed += 1
        else:
            filtered.append(r)
    return filtered, suppressed


# ── Main ───────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="CAB Audit — anchor structure scanner (formerly cab-lint)")
    parser.add_argument("path", type=Path, nargs="?", default=Path("."),
                        help="Path to anchor folder (default: current dir)")
    parser.add_argument("--level", type=int, default=5, help="Lint level 1-9 (default: 5)")
    parser.add_argument("--type", dest="anchor_type", help="Override detected type")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--show-exceptions", action="store_true",
                        help="Show suppressed warnings")
    parser.add_argument("--private", action="store_true",
                        help="Include private items in warnings (excluded by default)")
    parser.add_argument("--pub-only", action="store_true",
                        help="Only warn about pub items (stricter filter)")
    args = parser.parse_args()

    path = args.path.resolve()
    if not path.is_dir():
        print(f"Error: {path} is not a directory", file=sys.stderr)
        sys.exit(1)

    # Detect or override type
    if args.anchor_type:
        try:
            atype = AnchorType(args.anchor_type)
        except ValueError:
            print(f"Error: unknown type '{args.anchor_type}'", file=sys.stderr)
            sys.exit(1)
    else:
        atype = detect_type(path)

    anchor = Anchor(path=path, anchor_type=atype)
    results: list[LintResult] = []

    # Phase 0: Structural lint (levels 1-4)
    if args.verbose:
        print(f"Linting: {anchor.folder_name} (type: {atype.value}, level: {args.level})")

    results.extend(lint_structure(anchor, args.level))

    # Phase 1-3: Module doc comparison (level 5+, Code anchors only)
    if args.level >= 5 and anchor.anchor_type == AnchorType.CODE and anchor.code_path:
        cache_dir = anchor.path / ".skl" / "lint" / "source-cache"

        # Phase 1: Scan
        if args.verbose:
            print(f"\nScanning source: {anchor.code_path}")
        parsed = scan_source_tree(anchor.code_path, cache_dir, verbose=args.verbose)
        if args.verbose:
            print(f"  Parsed {parsed} files (cached others)")

        # Phase 2: Load
        source_modules = load_source_modules(cache_dir)
        doc_modules = load_doc_modules(anchor.dev_folder, anchor.name)

        if args.verbose:
            src_classes = sum(len(m.classes) for m in source_modules)
            doc_classes = sum(len(m.classes) for m in doc_modules)
            print(f"  Source: {len(source_modules)} modules, {src_classes} classes")
            print(f"  Docs: {len(doc_modules)} modules, {doc_classes} classes")

        # Phase 3: Compare
        if source_modules and doc_modules:
            results.extend(compare_modules(
                source_modules, doc_modules,
                include_private=args.private,
                pub_only=args.pub_only,
                lint_level=args.level,
            ))
        elif source_modules and not doc_modules:
            results.append(LintResult(
                "no-module-docs", 5, Status.CONCERN,
                f"Source has {len(source_modules)} modules but no module docs in Dev folder",
            ))
        elif not source_modules and doc_modules:
            results.append(LintResult(
                "no-source-cache", 5, Status.CONCERN,
                "Module docs exist but no source files were parsed",
            ))

    # Load and apply system suppressions (global, not counted in report)
    system_supp_file = Path.home() / ".claude" / "skills" / "cab" / "LINT User Docs" / "cab-lint-system-suppressions.md"
    system_exceptions = load_exceptions_from_file(system_supp_file)
    results, sys_suppressed = filter_exceptions(results, system_exceptions)

    # Load and apply project exceptions (per-anchor, counted)
    exceptions = load_exceptions(path)
    results, suppressed = filter_exceptions(results, exceptions)

    # Output
    if args.json:
        print(report_json(anchor, results, args.level))
    else:
        output = report_markdown(anchor, results, args.level)

        # Compact summary line
        concerns = sum(1 for r in results if r.status == Status.CONCERN)
        failed = sum(1 for r in results if r.status == Status.FAIL)
        parts = []
        if failed:
            parts.append(f"{failed} fail")
        if concerns:
            parts.append(f"{concerns} warnings")
        if suppressed:
            parts.append(f"{suppressed} excepted")
        if sys_suppressed:
            parts.append(f"{sys_suppressed} system")
        if parts:
            output += f"\n{', '.join(parts)}"

        if args.show_exceptions and exceptions:
            output += f"\n\n### Exceptions ({len(exceptions)})"
            for exc in exceptions:
                target = f" {exc.target}" if exc.target else ""
                output += f"\n  · {exc.module}{target} [{exc.rule}] — {exc.reason}"
        print(output)

    g = gate(results)
    sys.exit(2 if g == "FAIL" else 1 if g == "CONCERNS" else 0)


if __name__ == "__main__":
    main()
