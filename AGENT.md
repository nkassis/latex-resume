# AGENT.md

Notes for coding agents working in this repo.

## Public repo rules
- The repo is public. Never put target company names, job postings, or recruiter names in files or commit messages.
- Never put a phone number in any file. `\phone` is empty in every `variants/*/Resume.tex`; `make private` injects it from `.env` (gitignored, see `.env.example`) into `private/<variant>/` (gitignored). `dist/` and GitHub Pages never carry it.
- Do not change the LaTeX macros, layout, or fonts unless the user explicitly asks.
- Every variant must stay at 2 pages with no Overfull/Underfull hbox warnings.

## Layout and variants
- `variants/<variant>/Resume.tex`: one folder per variant. `general` is canonical; `insurance` is the insurance-oriented variant.
- Each variant is a standalone copy. Edits that apply to "every variant" must be made in each `variants/*/Resume.tex`.
- The Makefile discovers variants from the folders under `variants/`. Do not hardcode a list, and do not name a variant `all`, `clean` or `private`.
- Every variant outputs `dist/<variant>/resume-nicolas-kassis.{pdf,txt,md}`. Aux files go to `build/<variant>/`.
- Only `general` is published to GitHub Pages, and only `dist/general/` is committed; `dist/*` for other variants is gitignored. Never add a tailored variant to the Pages `_site` in `.github/workflows/build.yml`.
- `tools/tex2md.py <in.tex> <out.md>` converts the custom macros to Markdown; extend its dispatch tables if new macros are added.

## Build and verify
```sh
make clean && make                                            # all variants
make <variant>                                                # one variant
grep -nE "Overfull|Underfull" build/*/Resume.log              # expect no output
for f in dist/*/resume-nicolas-kassis.pdf; do pdfinfo "$f" | grep Pages; done   # expect 2 each
```
- Rebuild and commit `dist/general/` whenever `variants/general/Resume.tex` changes.
- CI runs `make clean && make` (TeX Live from apt) and uploads `dist/` as the build artifact.
