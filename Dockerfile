# This Dockerfile builds the Rechtssammlung by making use of the Makefile
# in the Rechtssammlung folder. The environment variable $MAKE_TARGET
# specifies the target in that Makefile and $OUTPUT specifies where the
# compiled PDFs will be copied to.

ARG UID=1000

# Build mdbook from source
FROM rust:1.77-slim-bookworm as mdbook

# renovate: datasource=crate depName=mdbook
ENV MDBOOK_VERSION 0.4.25
RUN cargo install mdbook --version ${MDBOOK_VERSION} --target x86_64-unknown-linux-gnu


# Setup the container to actually build the rechtssammlung
FROM texlive/texlive:latest as build

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y python3-pip inkscape

# Install mdbook
COPY --from=mdbook /usr/local/cargo/bin/mdbook /usr/bin/mdbook
RUN mdbook --version
WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt --break-system-packages

COPY . .

# Invocation through shell is ok as we are only building stuff in production.
CMD make OUT_PATH=$OUTPUT $MAKE_TARGET && chown -R $UID:$UID $OUTPUT
