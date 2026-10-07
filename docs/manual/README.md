# ALPR Evader 3x manual

`alpr-evader.manual.json` is the editable source. `index.html` is the generated, standalone manual operators and
contributors can open directly in a browser. The project's purpose-specific Markdown documents remain authoritative;
the manual synthesizes them into a what/how/why reading path (D-011).

Validate and rebuild from the repository root:

```bash
python3 tools/3x_manual.py check docs/manual/alpr-evader.manual.json
python3 tools/3x_manual.py build docs/manual/alpr-evader.manual.json --output docs/manual/index.html
```

`python3 tools/check_docs.py` also validates the source and fails when the committed HTML does not match it.

The generator and schema are adapted from the 3x Documentation Scheme. They are used under the MIT terms in
`3X-LICENSE`.
