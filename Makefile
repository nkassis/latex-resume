.PHONY: all pdf txt clean distclean

all: pdf txt

pdf: Resume.pdf

Resume.pdf: Resume.tex
	pdflatex -interaction=nonstopmode Resume.tex
	pdflatex -interaction=nonstopmode Resume.tex

txt: Resume.txt

Resume.txt: Resume.pdf
	pdftotext -layout Resume.pdf Resume.txt

clean:
	rm -f Resume.aux Resume.log Resume.out Resume.fdb_latexmk Resume.fls Resume.synctex.gz Resume.toc

distclean: clean
	rm -f Resume.pdf Resume.txt
