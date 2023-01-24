# This Dockerfile builds the Rechtssammlung by making use of the Makefile
# in the Rechtssammlung folder. The environment variable $MAKE_TARGET
# specifies the target in that Makefile and $OUTPUT specifies where the
# compiled PDFs will be copied to.

FROM texlive/texlive:latest as build

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y python3-pip

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .


# Copy everything to output
CMD make OUT_PATH=$OUTPUT $MAKE_TARGET
