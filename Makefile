# Every folder under variants/ is a variant (folders named "all" or "clean" are not allowed).
VARIANTS := $(notdir $(patsubst %/,%,$(wildcard variants/*/)))
OUT := resume-nicolas-kassis

.PHONY: all clean $(VARIANTS)
# Keep the PDFs; make would otherwise delete them as intermediates of the .txt rule.
.SECONDARY: $(foreach v,$(VARIANTS),dist/$(v)/$(OUT).pdf)

all: $(VARIANTS)

$(VARIANTS): %: dist/%/$(OUT).pdf dist/%/$(OUT).txt dist/%/$(OUT).md

# Aux files stay in build/<variant>/ so variants never collide.
dist/%/$(OUT).pdf: variants/%/Resume.tex
	mkdir -p build/$* dist/$*
	pdflatex -interaction=nonstopmode -output-directory=build/$* $<
	pdflatex -interaction=nonstopmode -output-directory=build/$* $<
	cp build/$*/Resume.pdf $@

dist/%/$(OUT).txt: dist/%/$(OUT).pdf
	pdftotext -layout $< $@

dist/%/$(OUT).md: variants/%/Resume.tex tools/tex2md.py
	mkdir -p dist/$*
	python3 tools/tex2md.py $< $@

clean:
	rm -rf build dist
