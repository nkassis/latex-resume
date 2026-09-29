# Nicolas Kassis — Résumé

LaTeX source, compiled PDF, and plaintext version of my résumé.

- **PDF:** [`Resume.pdf`](Resume.pdf) — also published at <https://nkassis.github.io/latex-resume/Resume.pdf>
- **Plaintext:** [`Resume.txt`](Resume.txt) — for paste-in application forms
- **Source:** [`Resume.tex`](Resume.tex)

## Build

Requires TeX Live (with `tgpagella`, `hyperref`, `microtype`, `cmap`, `hyphenat`) and `poppler-utils`.

```sh
make          # builds Resume.pdf and Resume.txt
make pdf      # PDF only
make txt      # regenerate plaintext from PDF
make clean    # remove LaTeX aux files
make distclean # also remove Resume.pdf and Resume.txt
```

## CI

`.github/workflows/build.yml` builds the PDF on every push to `master` and publishes it via GitHub Pages so job applications can point at a stable URL that always reflects `master`.

## License

MIT — the template scaffolding and prose bullets are free to reuse. See [`LICENSE`](LICENSE).
