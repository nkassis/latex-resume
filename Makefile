.PHONY: all pdf txt md clean distclean

all: pdf txt md

pdf: Resume.pdf

Resume.pdf: Resume.tex
	pdflatex -interaction=nonstopmode Resume.tex
	pdflatex -interaction=nonstopmode Resume.tex

txt: Resume.txt

Resume.txt: Resume.pdf
	pdftotext -layout Resume.pdf Resume.txt

md: Resume.md

Resume.md: Resume.tex tex2md.py
	python3 tex2md.py Resume.tex Resume.md

clean:
	rm -f Resume.aux Resume.log Resume.out Resume.fdb_latexmk Resume.fls Resume.synctex.gz Resume.toc

distclean: clean
	rm -f Resume.pdf Resume.txt Resume.md
