# AGENT.md

Notes for coding agents working in this repo.

## Public repo rules
- The repo is public. Never put target company names, job postings, or recruiter names in files or commit messages.
- Do not change the LaTeX macros, layout, or fonts unless the user explicitly asks.
- Every variant must stay at 2 pages with no Overfull/Underfull hbox warnings.

## Variants
- `Resume.tex` is the canonical general version.
- `Resume-insurance.tex` is the insurance-oriented variant (a standalone copy; edits that apply to "every variant" must be made in both).
- Variants are listed in `VARIANTS` in the `Makefile` and compiled individually in `.github/workflows/build.yml`. Update both when adding one.

## Build and verify
```sh
make                                             # PDF + TXT + MD for every variant
grep -nE "Overfull|Underfull" Resume*.log        # expect no output
for f in Resume*.pdf; do pdfinfo "$f" | grep Pages; done   # expect 2 each
```
- `tex2md.py <in.tex> <out.md>` converts the custom macros to Markdown; extend its dispatch tables if new macros are added.
- Generated `*.pdf`, `*.txt`, `*.md` are committed; rebuild them whenever a `.tex` changes.
