###############################################################################
# Makefile for the VSETH-Rechtssammlung
#
# Authors: Michal Sudwoj, Manuel Hässig
#
# Builds can be done locally using the targets "all", "mdbook", "pdf", and "latex".
# In case of missing depedencies or fear of clutter (or for the lulz) builds
# can be performed in a docker container via the "docker" target. Per default
# the docker target builds the target "all" and outputs the results in the
# usual output folder.
#
# Argument variables:
#  - OUT_PATH: specifies folder where the build files are written to
#  - DOCKER_IMAGE_NAME: name of the docker image used for docker builds
#  - DOCKER_MAKE_TARGET: make target executed in a docker build (default: all)
#
###############################################################################


OUT_PATH ?= $(PWD)/out
PDF_PATH = ${OUT_PATH}/pdf
CSV_PATH = ${OUT_PATH}/csv
LATEX_PATH = ${OUT_PATH}/latex
MDBOOK_PATH = ${OUT_PATH}/mdbook
NAVBAR_PATH = ${OUT_PATH}/navbar
HTML_PATH = ${MDBOOK_PATH}/book
ASSET_PATH = $(PWD)/assets

DOCKER_IMAGE_NAME ?= reglemente-builder
DOCKER_INTERNAL_OUT_PATH = /out
DOCKER_MAKE_TARGET ?= all

LATEXOPTS = -interaction=nonstopmode -shell-escape -file-line-error
LATEXMKOPTS = -outdir=${PDF_PATH} -norc -f -latexoption=${LATEXOPTS}

# We extract the list of sources from VSETH_Rechtssammlung.xml. This way we don't need to make changes twice.
SRCS = VSETH_Rechtssammlung.xml $(shell grep href= VSETH_Rechtssammlung.xml | sed -r 's/.*href="(.+)".*/\1/' | tr "\n" " ")

MDBOOK_ASSETS = $(shell find ${ASSET_PATH}/mdbook -type f)


all: html pdf

csv: ${SRCS} templates/csv/$(wildcard *.csv.j2) $(wildcard *.py)
	python3 main.py generate --asset-path ${ASSET_PATH} --format csv --output-folder ${CSV_PATH} $<

# We build the HTML representation by building an mdbook
html: mdbook
	mdbook build ${MDBOOK_PATH}

# An mdbook is only made from the entire Rechtssammlung.
# VSETH_Rechtssammlung.xml is the first file in ${SRCS}. Therefore, $< will only build that file.
mdbook: ${SRCS} templates/mdbook/$(wildcard *.md.j2) $(wildcard *.py) | mdbook-init
	python3 main.py generate --asset-path ${ASSET_PATH} --format mdbook --output-folder ${MDBOOK_PATH} $<

# Initialize the mdbook folder by copying config files and assets
mdbook-init: config/book.toml $(wildcard ${ASSET_PATH}/mdbook/*) ${MDBOOK_ASSETS} clean-mdbook navbar
	mkdir -p ${MDBOOK_PATH}
	cp config/book.toml ${MDBOOK_PATH}/
	cp -r ${ASSET_PATH}/mdbook/theme ${MDBOOK_PATH}/vseth
	cp ${ASSET_PATH}/mdbook/*.css ${MDBOOK_PATH}/
	cp ${NAVBAR_PATH}/*.hbs ${MDBOOK_PATH}/vseth/

navbar: templates/navbar/$(wildcard *.html.j2) $(wildcard *.py)
	mkdir -p ${NAVBAR_PATH}
	python3 main.py generate --asset-path ${ASSET_PATH} --format navbar --output-folder ${NAVBAR_PATH} $<

# PDFs are also built individually. Therefore, we use suffix replacement and pattern rules to build
# all files individually.
tex: ${SRCS:.xml=.tex}

pdf: ${SRCS:.xml=.pdf}

%.tex: %.xml templates/latex/$(wildcard *.tex.j2) $(wildcard *.py)
	python3 main.py generate --asset-path ${ASSET_PATH} --format latex --output ${LATEX_PATH} $<

%.pdf: %.tex
	latexmk -pdf ${LATEXMKOPTS} ${LATEX_PATH}/$<

.PHONY: test
test: all
	mdbook serve ${MDBOOK_PATH}

.PHONY: build-docker
build-docker: docker
	mkdir -p $(OUT_PATH)
	docker run \
		--rm \
		-e OUTPUT=$(DOCKER_INTERNAL_OUT_PATH) \
		-e DOCKER_MAKE_TARGET=$(DOCKER_MAKE_TARGET) \
		-e UID=$(shell id -u) \
		-e GID=$(shell id -g) \
		-v $(OUT_PATH):$(DOCKER_INTERNAL_OUT_PATH) \
		$(DOCKER_IMAGE_NAME)

docker: Dockerfile
	docker build . -t $(DOCKER_IMAGE_NAME)

.PHONY: clean
clean:
	cd ${LATEX_PATH} && latexmk -c ${LATEXMKOPTS} && cd $(PWD)

.PHONY: clean-mdbook
clean-mdbook:
	${RM} -r $(wildcard ${MDBOOK_PATH}/*)
	${RM} -r $(wildcard ${NAVBAR_PATH}/*)

.PHONY: dist-clean
dist-clean: clean-mdbook
	${RM} -r $(wildcard ${PDF_PATH}/*)
	${RM} -r $(wildcard ${LATEX_PATH}/*)