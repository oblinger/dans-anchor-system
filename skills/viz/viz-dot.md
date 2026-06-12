# /viz dot — Graphviz DOT diagrams

Generate box/arrow graphs, system diagrams, decision trees, org charts, dependency graphs from DOT source. Output is `.png`, `.pdf`, or `.svg`.

## Tool

`dot` — installed via `brew install graphviz`. Verify with `dot -V`.

## Source format

`.dot` text file. Example:

```
digraph SystemArchitecture {
  rankdir=LR;
  Frontend -> API -> Database;
  API -> Cache;
}
```

Claude generates the `.dot` source from a natural-language description, then runs `dot` to render.

## Usage

```bash
# PNG (default)
dot -Tpng source.dot -o out.png

# PDF
dot -Tpdf source.dot -o out.pdf

# SVG (vector)
dot -Tsvg source.dot -o out.svg
```

Default output goes to `~/ob/data/MyDesk/{slug-from-prompt}-{YYYY-MM-DD-HHMM}.png` per the cross-cutting `/viz` default-location convention in [[SKILL]] § Default output.

## When to use vs Mermaid

Both tools cover overlapping ground. Pick by:
- **Quick flowchart / sequence / gantt** → Mermaid (less verbose syntax, native markdown rendering).
- **Complex graphs with custom styling, layout control, ranks, clusters** → Graphviz DOT (more powerful layout engine, finer control).
- **Org charts, dependency graphs, state machines** → Graphviz DOT (its strength).
- **Markdown-deliverable** → Mermaid wins on portability (renders natively in GitHub/etc).

## Workflow

1. **Decide between Mermaid and Graphviz** based on the criteria above.
2. **Generate `.dot` source** as a text file.
3. **Render** via `dot` with appropriate `-T` format flag.
4. **Print output path**.

## Verification

```bash
echo 'digraph G { A -> B -> C; A -> D; }' > /tmp/viz-dot-test.dot
dot -Tpng /tmp/viz-dot-test.dot -o /tmp/viz-dot-test.png
open /tmp/viz-dot-test.png
```
