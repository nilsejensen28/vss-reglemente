#! /usr/bin/env python
from lxml import etree
from jinja2 import Environment, FileSystemLoader
from argparse import ArgumentParser
from datetime import date
import json
import os
import pathlib
import re
import urllib

import bylaws

def main():
    parser = ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--output-folder", required=True)
    parser.add_argument("-f", "--format", choices=["mdbook", "latex", "navbar", "csv"], required=True)
    parser.add_argument("-a", "--asset-path", type=pathlib.Path, required=True)
    args = parser.parse_args()

    # create output folder
    os.makedirs(args.output_folder, exist_ok=True)



    jinja_env = Environment(
        loader=FileSystemLoader("templates/{}".format(args.format)),
        keep_trailing_newline=False,
    )
    jinja_env.filters['num2letter'] = num2letter
    jinja_env.filters['num2latin'] = num2latin
    jinja_env.filters['format_date'] = format_date

    match args.format:
        case "mdbook":
            rsvseth = bylaws.parse(args.input)
            rsvseth.collect_footnotes_pass()
            rsvseth.number_footnotes_pass()
            # Forbid making an mdbook with only one regulation.
            if isinstance(rsvseth, bylaws.Regulation):
                raise RuntimeError("An mdbook must always be made for the entire Rechtssammlung")

            summary_template = jinja_env.get_template("summary.md.j2")
            bylaws_template = jinja_env.get_template("bylaws.md.j2")
            regl_template = jinja_env.get_template("regulation.md.j2")
            with open("{}/SUMMARY.md".format(args.output_folder), "w", encoding="utf-8") as f:
                f.write(summary_template.render(bylaws=rsvseth))
            with open("{}/{}.md".format(args.output_folder, rsvseth.filename), "w", encoding="utf-8") as f:
                f.write(bylaws_template.render(bylaws=rsvseth))
            for regl in rsvseth.regulations:
                with open("{}/{}.md".format(args.output_folder, regl.filename), "w", encoding="utf-8") as f:
                    f.write(regl_template.render(regl=regl))

        case "latex":
            # adjust start and end strings to be compatible with LaTeX
            jinja_env.block_start_string = "((*"
            jinja_env.block_end_string = "*))"
            jinja_env.variable_start_string = "(("
            jinja_env.variable_end_string = "))"
            jinja_env.comment_start_string = "((#"
            jinja_env.comment_end_string = "#))"
            jinja_env.filters['escape_tex'] = escape_tex

            rsvseth = bylaws.parse(args.input)

            bylaws_template = jinja_env.get_template("bylaws.tex.j2")
            regl_template = jinja_env.get_template("regulations.tex.j2")
            if isinstance(rsvseth, bylaws.Bylaws):
                with open("{}/VSETH_Rechtssammlung.tex".format(args.output_folder), "w", encoding="utf-8") as f:
                    f.write(bylaws_template.render(bylaws=rsvseth, asset_path=args.asset_path))
            else:
                regl = rsvseth
                with open("{}/{}.tex".format(args.output_folder, regl.filename), "w", encoding="utf-8") as f:
                    f.write(regl_template.render(regl=regl, asset_path=args.asset_path))

        case "csv":
            rsvseth = bylaws.parse(args.input)

            csv_template = jinja_env.get_template("regulation.csv.j2")

            if isinstance(rsvseth, bylaws.Bylaws):
                for regl in rsvseth.regulations:
                    with open("{}/{}.csv".format(args.output_folder, regl.filename), "w", encoding="utf-8") as f:
                        f.write(csv_template.render(regl=regl))
            else:
                regl = rsvseth
                with open("{}/{}.csv".format(args.output_folder, regl.filename), "w", encoding="utf-8") as f:
                    f.write(csv_template.render(regl=regl))

        case "navbar":
            navbar_template = jinja_env.get_template("navbar.html.j2")
            with urllib.request.urlopen("https://static.vseth.ethz.ch/assets/vseth-0100-verband/config.json") as response:
                externalNavbarData = json.loads(response.read())
                with open("{}/header.hbs".format(args.output_folder), "w", encoding="utf-8") as f:
                    f.write(navbar_template.render(primaryNavBarData=externalNavbarData))
        case _:
            raise NotImplementedError()

# Filter for latex escaping
# Source: https://stackoverflow.com/questions/43495728/escaping-slashes-for-jinja2-and-latex
LATEX_SUBS = (
    (re.compile(r'\\'), r'\\textbackslash'),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
    (re.compile(r'/'), r'\/')
)

def escape_tex(value):
    newval = str(value)
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
    return newval

# Filter to convert numbers to lowercase letters. Zero is converted to the empty string.
def num2letter(counter):
    if counter < 0:
        raise ValueError("expected positive value")
    if counter > 26:
        raise ValueError("cannot convert numbers larger than 26 to letters")

    if counter == 0:
        return ""
    else:
        return chr(ord('`') + counter)

# Filter to convert numbers to latin numerals. Zero is converted to the empty string.
def num2latin(counter):
    if counter < 0:
        raise ValueError("expected positive value")
    if counter > 14:
        raise ValueError("cannot convert numbers larger than 14 to latin numeral (if you see this, the Rechtssammlung is in big trouble...)")

    return ["", "bis", "ter", "quarter", "quinquies", "sexies", "septies", "octies", "novies", "decies", "undecies", "duodecies", "terdecies", "quaterdecies"][counter]
    
def format_date(date: date):
    return date.strftime("%d.%m.%Y")

if __name__ == "__main__":
    main()
