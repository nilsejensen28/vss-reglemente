#! /usr/bin/env python
from lxml import etree
from jinja2 import Environment, PackageLoader
from argparse import ArgumentParser
import os

import bylaws

def main():
    parser = ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--output-folder", required=True)
    parser.add_argument("-f", "--format", choices=["mdbook"], required=True)
    args = parser.parse_args()

    # create output folder
    os.makedirs(args.output_folder, exist_ok=True)

    rsvseth = bylaws.parse(args.input)


    jinja_env = Environment(
        loader=PackageLoader("templates", args.format),
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

        case _:
            raise NotImplementedError()



if __name__ == "__main__":
    main()
