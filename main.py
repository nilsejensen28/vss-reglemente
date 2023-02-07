#! /usr/bin/env python
from lxml import etree
from jinja2 import Environment, FileSystemLoader
from argparse import ArgumentParser
import os
import pathlib
import re

import bylaws

def main():
    parser = ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--output-folder", required=True)
    parser.add_argument("-f", "--format", choices=["mdbook", "latex"], required=True)
    parser.add_argument("-a", "--asset-path", type=pathlib.Path, required=True)
    args = parser.parse_args()

    # create output folder
    os.makedirs(args.output_folder, exist_ok=True)

    rsvseth = bylaws.parse(args.input)


    jinja_env = Environment(
        loader=FileSystemLoader("templates/{}".format(args.format)),
        keep_trailing_newline=False,
    )

    match args.format:
        case "mdbook":
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
                with open("{}/{}.md".format(args.output_folder, regl.id), "w", encoding="utf-8") as f:
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

            bylaws_template = jinja_env.get_template("bylaws.tex.j2")
            regl_template = jinja_env.get_template("regulations.tex.j2")
            if isinstance(rsvseth, bylaws.Bylaws):
                with open("{}/VSETH_Rechtssammlung.tex".format(args.output_folder), "w", encoding="utf-8") as f:
                    f.write(bylaws_template.render(bylaws=rsvseth, asset_path=args.asset_path))
            else:
                regl = rsvseth
                with open("{}/{}.tex".format(args.output_folder, regl.filename), "w", encoding="utf-8") as f:
                    f.write(regl_template.render(regl=regl, asset_path=args.asset_path))
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

if __name__ == "__main__":
    main()
