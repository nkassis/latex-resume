# Nicolas Kassis — Résumé

LaTeX source, compiled PDF, and plaintext version of my résumé.

- **PDF:** [`dist/general/resume-nicolas-kassis.pdf`](dist/general/resume-nicolas-kassis.pdf) — also published at <https://nkassis.github.io/latex-resume/Resume.pdf>
- **Plaintext:** [`dist/general/resume-nicolas-kassis.txt`](dist/general/resume-nicolas-kassis.txt) — for paste-in application forms
- **Source:** [`variants/general/Resume.tex`](variants/general/Resume.tex)

## Layout

```
variants/<variant>/Resume.tex           # one folder per variant
tools/tex2md.py                         # .tex -> Markdown converter
build/<variant>/                        # LaTeX aux files (ignored)
dist/<variant>/resume-nicolas-kassis.*  # PDF, TXT, MD outputs
```

### Variants

| Variant | Source |
| --- | --- |
| `general` (canonical) | [`variants/general/Resume.tex`](variants/general/Resume.tex) |
| `insurance` | [`variants/insurance/Resume.tex`](variants/insurance/Resume.tex) |
| `platform` | [`variants/platform/Resume.tex`](variants/platform/Resume.tex) |
| `fintech` | [`variants/fintech/Resume.tex`](variants/fintech/Resume.tex) |

Rules:

- Every variant builds to the same neutral filename: `dist/<variant>/resume-nicolas-kassis.{pdf,txt,md}`.
- Only the `general` variant is published to GitHub Pages, and only its outputs are committed (`dist/general/`). Other variants' outputs are gitignored and available from the CI build artifact.
- Each variant is a standalone copy of the general `Resume.tex`. A fix that applies everywhere must be made in every variant.
- To add a variant, create `variants/<name>/Resume.tex`. The Makefile discovers it automatically, and CI builds it via `make`.

## Build

Requires TeX Live (with `tgpagella`, `hyperref`, `microtype`, `cmap`, `hyphenat`), `poppler-utils`, and Python 3.

```sh
make            # build PDF, TXT, and MD for every variant
make general    # build one variant (any folder name under variants/)
make insurance
make private    # same files for every variant, with the phone number, in private/ (gitignored)
make private-insurance   # one variant
make clean      # remove build/, dist/ and private/ (including the committed general outputs; rerun make)
```

### Phone number

The phone number is never committed. Copy `.env.example` to `.env` (gitignored) and set `RESUME_PHONE`; `make private` builds `private/<variant>/resume-nicolas-kassis.{pdf,txt,md}` with the number for application uploads. Everything else, including `dist/`, the committed outputs and the GitHub Pages copy, leaves it out.

## CI

`.github/workflows/build.yml` runs `make` on every push to `master`. It uploads the whole `dist/` directory as the `resume` build artifact, so you can download any variant. It publishes only the general variant to GitHub Pages: `Resume.pdf` (stable URL), `resume-nicolas-kassis.pdf`, `Resume.txt`, and an `index.html` that redirects to `Resume.pdf`.

## License

MIT — the template scaffolding and prose bullets are free to reuse. See [`LICENSE`](LICENSE).
