OUT_PATH ?= $(PWD)/out
PDF_PATH = ${OUT_PATH}/pdf
LATEX_PATH = ${OUT_PATH}/latex
MDBOOK_PATH = ${OUT_PATH}/mdbook
ASSET_PATH = $(PWD)/assets

DOCKER_IMAGE_NAME ?= reglemente-builder
DOCKER_INTERNAL_OUT_PATH = /out
MAKE_TARGET ?= all

LATEXOPTS = -interaction=nonstopmode -shell-escape -file-line-error
LATEXMKOPTS = -outdir=${PDF_PATH} -norc -use-make -latexoption=${LATEXOPTS}

# We extraxt the list of sources from VSETH_Rechtssammlung.xml. This way we don't need to make changes twice.
SRCS = VSETH_Rechtssammlung.xml $(shell grep href= VSETH_Rechtssammlung.xml | sed -r 's/.*href="(.+)".*/\1/' | tr "\n" " ")


.PHONY: all
all: mdbook pdf

.PHONY: mdbook
mdbook: ${SRCS} templates/mdbook/$(wildcard *.md.j2) $(wildcard *.py)
	python3 main.py --asset-path ${ASSET_PATH} --format mdbook --output-folder ${MDBOOK_PATH} $<

.PHONY: tex
%.tex: ${SRCS} templates/latex/$(wildcard *.tex.j2) $(wildcard *.py)
	python3 main.py --asset-path ${ASSET_PATH} --format latex --output ${LATEX_PATH} $<

.PHONY: pdf
pdf: ${SRCS:.xml=.pdf}

%.pdf: %.tex | tex
	latexmk -pdf ${LATEXMKOPTS} ${LATEX_PATH}/$<

.PHONY: docker
docker: Dockerfile
	docker build . -t $(DOCKER_IMAGE_NAME)
	docker run \
		--rm \
		-e OUTPUT=$(DOCKER_INTERNAL_OUT_PATH) \
		-e MAKE_TARGET=$(MAKE_TARGET) \
		-v $(OUT_PATH):$(DOCKER_INTERNAL_OUT_PATH) \
		$(DOCKER_IMAGE_NAME)

.PHONY: clean
clean:
	cd ${LATEX_PATH} && latexmk -c ${LATEXMKOPTS} && cd $(PWD)

.PHONY: dist-clean
dist-clean:
	cd ${LATEX_PATH} && latexmk -C ${LATEXMKOPTS} || true && cd $(PWD)
	${RM} -r $(wildcard ${PDF_PATH}/*)
	${RM} -r $(wildcard ${LATEX_PATH}/*)
	${RM} -r $(wildcard ${MDBOOK_PATH}/*)