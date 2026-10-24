# Nicolas Kassis — Résumé

LaTeX source, compiled PDF, and plaintext version of my résumé.

- **PDF:** [`Resume.pdf`](Resume.pdf) — also published at <https://nkassis.github.io/latex-resume/Resume.pdf>
- **Plaintext:** [`Resume.txt`](Resume.txt) — for paste-in application forms
- **Source:** [`Resume.tex`](Resume.tex)

### Variants

| Variant | Source | Outputs |
| --- | --- | --- |
| General (canonical) | [`Resume.tex`](Resume.tex) | `Resume.pdf`, `Resume.txt`, `Resume.md` |
| Insurance-oriented | [`Resume-insurance.tex`](Resume-insurance.tex) | `Resume-insurance.pdf`, `Resume-insurance.txt`, `Resume-insurance.md` |

Each variant is a standalone copy of `Resume.tex`. Fixes that apply everywhere must be made in every variant. To add a variant, append its basename to `VARIANTS` in the `Makefile` and add a compile step to `.github/workflows/build.yml`.

## Build

Requires TeX Live (with `tgpagella`, `hyperref`, `microtype`, `cmap`, `hyphenat`) and `poppler-utils`.

```sh
make           # builds PDF, TXT, and MD for every variant
make pdf       # PDFs only
make txt       # regenerate plaintext from PDFs
make md        # regenerate Markdown from .tex via tex2md.py
make Resume-insurance.pdf  # build a single variant
make clean     # remove LaTeX aux files
make distclean # also remove generated PDF/TXT/MD files
```

## CI

`.github/workflows/build.yml` builds every variant's PDF on every push to `master` and publishes it via GitHub Pages so job applications can point at a stable URL that always reflects `master`.

## License

MIT — the template scaffolding and prose bullets are free to reuse. See [`LICENSE`](LICENSE).
