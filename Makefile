SHELL := /bin/bash

SRCS = index.xml \
       01_Statuten.xml \
       11_MR.xml \
       12_FR.xml \
       13_Ausschuss.xml \
       13.01_FinA.xml \
       13.02_ITA.xml \
       13.03_SpEA.xml \
       21_Vorstand.xml \
       21.01_Vorstandspflichtenheft.xml \
       21.02_GS_Pflichtenheft.xml \
       21.03_AVES_Verordnung.xml \
       22_Komissionsreglement.xml \
       31_GPK_Reglement.xml \
       51_Fachvereinsreglement.xml \
       52_Vertretungsreglement.xml \
       53_StudOrg.xml \
       71_MOEhRe.xml \
       72_Finanzreglement.xml \
       72.01_Immobilienfonds.xml \
       72.02_Musikzimmerfonds.xml \
       72.03_Rechtsfonds.xml \
       72.04_ETH_Store_AG_Fonds.xml \
       72.05_Coronafonds.xml \
       73_Anstellungsreglement.xml \
       74_Datenschutzreglement.xml \
       75_Erscheinungsbildreglement.xml \
       76_Infrastrukturreglement.xml

.venv: requirements.txt
	python -m venv .venv
	source .venv/bin/activate && \
		pip install --upgrade pip && \
		pip install -r requirements.txt
	touch .venv

.PHONY: all
all: rst html sphinx json pdf

.PHONY: check
check: $(SRCS:xml=chk)

.PHONY: rst
rst: $(SRCS:xml=rst)

.PHONY: md
md: $(SRCS:xml=md)

.PHONY: html
html: $(SRCS:xml=html)

.PHONY: json
json: $(SRCS:xml=json)

.PHONY: tex
tex: $(SRCS:xml=tex)

.PHONY: pdf
pdf: $(SRCS:xml=pdf)

%.chk: %.xml .venv main.py check.py
	source .venv/bin/activate && \
		./main.py $< --format check
	touch $@

%.rst: %.xml .venv main.py rst_emitter.py | %.chk
	source .venv/bin/activate && \
		./main.py $< --format rst --output $@

%.md: %.xml .venv main.py | %.chk
	source .venv/bin/activate && \
		./main.py $< --format md --output $@

%.html: %.xml .venv main.py html_emitter.py | %.chk
	source .venv/bin/activate && \
		./main.py $< --format html --output $@

%.json: %.xml .venv main.py json_emitter.py | %.chk
	source .venv/bin/activate && \
		./main.py $< --format json --output $@

%.tex: %.xml .venv main.py latex_emitter.py | %.chk
	source .venv/bin/activate && \
		./main.py $< --format tex --output $@

%.pdf: %.tex
	latexmk -g -verbose -pdflua $<

sphinx: .venv conf.py $(SRCS:xml=rst)
	sphinx-build -b html . sphinx

.PHONY: clean
clean:
	GLOBIGNORE="Readme.md" && \
		rm -rf *.chk *.rst *.md *.html *.json sphinx *.aux *.fdb_latexmk *.fls *.log *.out *.pdf *.tex
