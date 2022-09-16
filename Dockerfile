FROM ubuntu:latest as metabuilder
SHELL ["/bin/bash", "-c"]
ARG DEBIAN_FRONTEND="noninteractive"

ARG TEXLIVE_INSTALL_PREFIX="/app/texlive"
ARG TEXLIVE_INSTALL_TEXDIR="${TEXLIVE_INSTALL_PREFIX}"
ENV PATH="${TEXLIVE_INSTALL_TEXDIR}/bin/x86_64-linux:${PATH}"

WORKDIR /app
COPY texlive.profile  install-tl/

RUN \
	set -euxo pipefail; \
	apt-get update; \
	apt-get install --assume-yes --no-install-recommends --no-install-suggests \
                texlive-luatex \
		python3-venv \
	; \
	python3 -m venv --upgrade-deps .venv; \
	apt-get remove --assume-yes --purge software-properties-common; \
	apt-get autoremove --assume-yes; \
	echo "Installing TeXLive..."; \
	apt-get install --assume-yes --no-install-recommends --no-install-suggests \
		ca-certificates \
		libencode-perl \
		perl-modules \
		wget \
		gpg \
	; \
	mkdir --parents install-tl; \
	cd install-tl; \
	wget --no-verbose \
		http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz \
	; \
	tar \
		--extract \
		--strip-components=1 \
		--gunzip \
		--file=install-tl-unx.tar.gz \
	; \
	./install-tl --profile texlive.profile; \
	cd ..; \
	rm --recursive --force install-tl; \
	echo "Installing Make..."; \
	apt-get install --assume-yes --no-install-recommends --no-install-suggests \
		make \
	; \
	echo "Cleaning up..."; \
	rm --recursive --force /var/lib/apt/lists/*;

FROM metabuilder as builder
ENV PATH="${PATH}"
WORKDIR /app

COPY requirements.txt .
COPY texlive.txt      .

RUN \
	set -euxo pipefail; \
	source .venv/bin/activate; \
	pip install -r requirements.txt; \
	apt-get update; \
	apt-get install --assume-yes --no-install-recommends --no-install-suggests \
		inkscape \
	; \
	rm --recursive --force /var/lib/apt/lists/*; \
	tlmgr install --reinstall $(cat texlive.txt); \
	luaotfload-tool --update;
