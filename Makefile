# Every folder under variants/ is a variant (folders named "all", "clean" or "private" are not allowed).
VARIANTS := $(notdir $(patsubst %/,%,$(wildcard variants/*/)))
OUT := resume-nicolas-kassis

# Local secrets. .env is gitignored; see .env.example.
-include .env
RESUME_PHONE := $(strip $(subst ",,$(RESUME_PHONE)))
PRIVATE := $(addprefix private-,$(VARIANTS))

.PHONY: all clean private $(VARIANTS) $(PRIVATE)
# Keep the PDFs; make would otherwise delete them as intermediates of the .txt rule.
.SECONDARY: $(foreach v,$(VARIANTS),dist/$(v)/$(OUT).pdf private/$(v)/$(OUT).pdf)

all: $(VARIANTS)

# Public outputs (dist/): no phone number. These are what gets committed and published.
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

# Private outputs (private/, gitignored): same files with the phone number from .env.
# Use these for application uploads. `make private` builds every variant,
# `make private-<variant>` builds one.
private: $(PRIVATE)

$(PRIVATE): private-%: private/%/$(OUT).pdf private/%/$(OUT).txt private/%/$(OUT).md

private/%/$(OUT).pdf: variants/%/Resume.tex tools/tex2md.py $(wildcard .env)
	@test -n "$(RESUME_PHONE)" || { echo "RESUME_PHONE is not set in .env (see .env.example)"; exit 1; }
	mkdir -p build/private/$* private/$*
	pdflatex -interaction=nonstopmode -output-directory=build/private/$* -jobname=Resume "\def\phone{$(RESUME_PHONE)}\input{$<}"
	pdflatex -interaction=nonstopmode -output-directory=build/private/$* -jobname=Resume "\def\phone{$(RESUME_PHONE)}\input{$<}"
	cp build/private/$*/Resume.pdf $@

private/%/$(OUT).txt: private/%/$(OUT).pdf
	pdftotext -layout $< $@

private/%/$(OUT).md: variants/%/Resume.tex tools/tex2md.py $(wildcard .env)
	@test -n "$(RESUME_PHONE)" || { echo "RESUME_PHONE is not set in .env (see .env.example)"; exit 1; }
	mkdir -p private/$*
	RESUME_PHONE="$(RESUME_PHONE)" python3 tools/tex2md.py $< $@

clean:
	rm -rf build dist private
