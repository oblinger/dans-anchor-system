"""Red-check the R-pathguard 01/03 store-vs-namesake narrowing against the REAL vault
corpus: every " Backlog.md" file is classified, and the verdict is compared to
ground truth (does `state` manage it?). Bodies are extracted live from the ruleset."""
import pathlib, re, sys, types

HERE = pathlib.Path(__file__).parent
RULESET = pathlib.Path("/Users/oblinger/ob/kmr/SYS/Bespoke/Skill Agent/dans-anchor-system/rulesets/R-pathguard.md")
VAULT = pathlib.Path.home() / "ob/kmr"

def load_body(rule_id):
    text = RULESET.read_text()
    m = re.search(r"^### RULE " + re.escape(rule_id) + r"\b.*?^```python\n(.*?)^```",
                  text, re.S | re.M)
    assert m, f"could not extract {rule_id}"
    ns = {}
    exec(compile(m.group(1), rule_id, "exec"), ns)
    return ns["body"]

def ctx_for(path, content=None):
    ev = types.SimpleNamespace(target=str(path), input={"content": content} if content else {})
    return types.SimpleNamespace(event=ev)

body01, body03 = load_body("R-pathguard-01"), load_body("R-pathguard-03")

files = [f for f in VAULT.rglob("* Backlog.md") if ".git" not in f.parts]
assert files, "no corpus found"

fails = 0
for f in sorted(files):
    head = f.read_text(errors="replace")[:800]
    truth = "state:backlog" in head          # ground truth: state manages it
    for label, body in (("01/Edit", body01), ("03/Write", body03)):
        denied = bool(body(ctx_for(f)))
        if denied != truth:
            print(f"FAIL {label}: denied={denied} truth={truth}  {f.relative_to(VAULT)}")
            fails += 1

print(f"\n{len(files)} corpus files x 2 rules — {len(files)*2 - fails} agree with ground truth")

# The three branches, on the file that motivated the fix.
facet = VAULT / "SYS/Bespoke/Skill Agent/dans-anchor-system/facets/DAS Backlog.md"
store = VAULT / "SYS/Staff/Tink/Tink Track/Tink Backlog.md"
checks = [
    ("facet is editable (Edit)",        not body01(ctx_for(facet))),
    ("facet is writable (Write)",       not body03(ctx_for(facet))),
    ("real store denied (Edit)",        bool(body01(ctx_for(store)))),
    ("real store denied (Write)",       bool(body03(ctx_for(store)))),
    ("new stamped store denied (Write)",
        bool(body03(ctx_for(VAULT / "nope/ZZZ Backlog.md", "# Z\n<!-- state:backlog ab -->\n")))),
    ("new namesake allowed (Write)",
        not body03(ctx_for(VAULT / "nope/ZZZ Backlog.md", "# Z\njust prose\n"))),
    ("nonexistent in Track denied (Write)",
        bool(body03(ctx_for(VAULT / "x/ZZZ Track/ZZZ Backlog.md", "prose")))),
    ("queries.md still denied",         bool(body03(ctx_for(VAULT / "a/TINK queries.md")))),
    ("Q.md still denied",               bool(body03(ctx_for(VAULT / "Q.md")))),
]
for name, ok in checks:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not ok: fails += 1

print("\n" + ("ALL PASS" if not fails else f"{fails} FAILURE(S)"))
sys.exit(1 if fails else 0)
