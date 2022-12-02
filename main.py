#! /usr/bin/env python
from lxml import etree
from jinja2 import Environment, FileSystemLoader
from argparse import ArgumentParser
import os

import bylaws

def main():
    parser = ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--output-folder", required=True)
    parser.add_argument("-f", "--format", choices=["mdbook", "latex"], required=True)
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
            summary_template = jinja_env.get_template("summary.md.j2")
            regl_template = jinja_env.get_template("regulation.md.j2")
            with open("{}/SUMMARY.md".format(args.output_folder), "w", encoding="utf-8") as f:
                f.write(summary_template.render(bylaws=rsvseth))
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

            bylaws_template = jinja_env.get_template("bylaws.tex.j2")
            regl_template = jinja_env.get_template("regulations.tex.j2")
            with open("{}/vseth-rechtssammlung.tex".format(args.output_folder), "w", encoding="utf-8") as f:
                f.write(bylaws_template.render(bylaws=rsvseth))
            for regl in rsvseth.regulations:
                with open("{}/{}.tex".format(args.output_folder, regl.filename), "w", encoding="utf-8") as f:
                    f.write(regl_template.render(regl=regl))
        case _:
            raise NotImplementedError()



if __name__ == "__main__":
    main()
