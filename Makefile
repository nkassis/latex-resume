.PHONY: all pdf txt md clean distclean

VARIANTS := Resume Resume-insurance
AUX_EXT := aux log out fdb_latexmk fls synctex.gz toc

all: pdf txt md

pdf: $(VARIANTS:=.pdf)

txt: $(VARIANTS:=.txt)

md: $(VARIANTS:=.md)

%.pdf: %.tex
	pdflatex -interaction=nonstopmode $<
	pdflatex -interaction=nonstopmode $<

%.txt: %.pdf
	pdftotext -layout $< $@

%.md: %.tex tex2md.py
	python3 tex2md.py $< $@

clean:
	rm -f $(foreach v,$(VARIANTS),$(addprefix $(v).,$(AUX_EXT)))

distclean: clean
	rm -f $(foreach v,$(VARIANTS),$(v).pdf $(v).txt $(v).md)
