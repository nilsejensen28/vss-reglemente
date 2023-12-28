# VSETH Rechtssammlung

The VSETH Rechtssammlung is generated from XML schemas into different formats (currently an 
[mdbook](https://rust-lang.github.io/mdBook/) and PDF via LaTeX). To edit the Rechtssammlung
you only need to know how to generate the documents and how the schema works (see Setup, Generating,
Schema). If you want to change other things see Developing.

[[_TOC_]]

## Overview
In this repo we maintain the VSETH Rechtssammlung as a collection of XML documents. These
XML documents allow us to easily generate different file formats from one source of truth.
Using [a Python script](main.py) we parse the XML structure into
[an abstract representation of Python classes](bylaws.py) which is then used to render
Jinja templates.

Currently, we support the generation of PDFs by generating and compiling LaTeX files, and
the generation of an [mdbook](https://rust-lang.github.io/mdBook), which serves as a searchable
website that allows for linking directly into articles.


## Setup
The easiest setup only needs [docker](https://www.docker.com/get-started/) and
[make](https://www.gnu.org/software/make/). Generally, this is what you want.


### Local Setup (docker-less)
 To build the Rechtssammlung without docker for better local testing you need the following software:
 - make
 - Python >=3.10
 - Python Pip
 - TexLive
 - latexmk (should be included in a TeXLive distribution)
 - inkscape
 - [mdbook](https://rust-lang.github.io/mdBook/)

First create a Python virtual environment with
```bash
$ python -m venv .venv
```
and activate the environment with
```bash
$ source .venv/bin/activate
```

Then, install the required python packages using
```bash
$ pip install -r requirements.txt
```
Now you are ready to go.


## Generating Documents
To generate all document formats using docker run `make build-docker`.

To generate all document formats locally without docker run `make`.

### Checking Document Generation without building locally
If you have no local setups (e.g. if you are a mere IA-Vorstand), you can commit your changes to 
a new branch and push the new branch. Then, you can check the output of the latest build for your
branch on [Teamcity](https://teamcity.vseth.ethz.ch/buildConfiguration/id0100Reglemente_Reglemente_Sip?mode=builds#all-projects)
(the builds take more than 5 minutes before they will fail in case you made a mistake).

## Adding a new regulation

 1. Create a new XML file. Use `00_example.xml` as a reference (or `22.00_Beispiel.xml` for committee regulations).
 2. Edit your file to match the decided contents.
 3. If all is well, add an entry of your newest file in `VSETH_Rechtssammlung.xml`.
 4. Generate all documents and check for errors (see above).
 5. Report any errors that you cannot fix to https://gitlab.ethz.ch/vseth/0100-Reglemente/reglemente/-/issues

## Adding minute links to existing change footnotes
Because some minutes take very long until they are available (e.g. MR), we provide a way to add
them easily after the fact. You can update the minute link for every change footnote of a single 
meeting date of a Gremium. Simply use the `insert-minutes` subcommand:
```bash
python main.py --gremium MR --date 2023-05-03 --minutes-link some-link
```
This will add the attribute `minutes_link="some-link"` to all change footnotes for the MR with
meeting date 03.05.2023 or update existsing `minutes_link` attributes to that link.

Note: If a Gremium holds multiple meetings on the same day where changes to the Rechtssammlung
are decided (extremely unlikely: only know case ao MR during Budget MR 2018), you need to add
the links manually in the XML files. This subcommand can not distinguish between different meetings
of the same Gremium on the same day.

## Troubleshooting

### Your text or link contains "&"
Unfortunately, XML uses "&" as an escape character. Therefore, you need to replace "&" with "&amp;" to make things work.
See 22.07_FC.xml for an example.
