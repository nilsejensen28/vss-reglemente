#! /usr/bin/env python
from jinja2 import Environment, FileSystemLoader
from argparse import ArgumentParser
from datetime import date
import json
import os
import pathlib
import re
import urllib

import bylaws
import logging

LANGUAGES = ["de", "fr"]


def main():
    logging.basicConfig(level=logging.INFO)
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    parser_gen = subparsers.add_parser(
        "generate", help="Generate documents in different formats")
    parser_gen.add_argument("input")
    parser_gen.add_argument("-o", "--output-folder", required=True)
    parser_gen.add_argument(
        "-f", "--format", choices=["mdbook", "latex", "navbar", "csv"], required=True)
    parser_gen.add_argument("-a", "--asset-path",
                            type=pathlib.Path, required=True)
    parser_gen.add_argument(
        "-l", "--language", choices=["de", "fr", "multiple"], required=True)
    parser_minutes = subparsers.add_parser(
        "insert-minutes", help="Insert minutes into the Rechtssammlung")
    parser_minutes.add_argument("-g", "--gremium", required=True)
    parser_minutes.add_argument("-d", "--date", required=True)
    parser_minutes.add_argument("-m", "--minutes-link", required=True)
    args = parser.parse_args()

    match args.subcommand:
        case "generate":
            generate(args)
        case "insert-minutes":
            insert_minutes(args)
        case _:
            raise NotImplementedError()


def generate(args):
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
            rsvss = bylaws.parse(args.input)

            # Mdbook needs manual numbering and footnote collection.
            rsvss.numbering_pass()
            rsvss.collect_footnotes_pass()
            rsvss.number_footnotes_pass()
            rsvss.latest_change_pass()

            # Forbid making an mdbook with only one regulation.
            if isinstance(rsvss, bylaws.Regulation):
                raise RuntimeError(
                    "An mdbook must always be made for the entire Rechtssammlung")

            summary_template = jinja_env.get_template("summary.md.j2")
            bylaws_template = jinja_env.get_template("bylaws.md.j2")
            regl_template = jinja_env.get_template("regulation.md.j2")
            with open("{}/SUMMARY.md".format(args.output_folder), "w", encoding="utf-8") as f:
                f.write(summary_template.render(bylaws=rsvss))
            with open("{}/{}.md".format(args.output_folder, rsvss.filename), "w", encoding="utf-8") as f:
                f.write(bylaws_template.render(bylaws=rsvss))
            for regl in rsvss.regulations:
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
            jinja_env.lstrip_blocks = True
            jinja_env.trim_blocks = True
            jinja_env.globals["GLOBAL_LANGUAGE"] = LANGUAGES[0]
            jinja_env.globals["GLOBAL_LANGUAGE_LIST"] = LANGUAGES
            jinja_env.filters['escape_tex'] = escape_tex

            rsvss = bylaws.parse(args.input)
            rsvss.numbering_pass()
            rsvss.latest_change_pass()

            bylaws_multilingual_template = jinja_env.get_template(
                "bylaws_multilingual.tex.j2")
            bylaws_template = jinja_env.get_template(
                "bylaws.tex.j2")
            regl_template = jinja_env.get_template(
                "regulations.tex.j2")
            regl_multilingual_template = jinja_env.get_template(
                "regulations_multilingual.tex.j2")
            if isinstance(rsvss, bylaws.Bylaws):
                # with open("{}/VSS_Rechtssammlung.tex".format(args.output_folder), "w", encoding="utf-8") as f:
                # f.write(bylaws_template.render(
                # bylaws=rsvss, asset_path=args.asset_path))
                # Check that we have at most two set languages
                if len(LANGUAGES) > 2:
                    jinja_env.globals["GLOBAL_LANGUAGE_LIST"] = ["de", "fr"]
                with open("{}/VSS_Rechtssammlung_multilingual.tex".format(args.output_folder), "w", encoding="utf-8") as f:
                    f.write(bylaws_multilingual_template.render(
                        bylaws=rsvss, asset_path=args.asset_path))
                for language in LANGUAGES:
                    jinja_env.globals["GLOBAL_LANGUAGE"] = language
                    with open("{}/VSS_Rechtssammlung_{}.tex".format(args.output_folder, language), "w", encoding="utf-8") as f:
                        f.write(bylaws_template.render(
                            bylaws=rsvss, asset_path=args.asset_path))
            else:
                regl = rsvss
                if len(LANGUAGES) > 2:
                    jinja_env.globals["GLOBAL_LANGUAGE_LIST"] = ["de", "fr"]
                with open("{}/{}_multilingual.tex".format(args.output_folder, regl.filename), "w", encoding="utf-8") as f:
                    f.write(regl_multilingual_template.render(
                        regl=regl, asset_path=args.asset_path))
                for language in LANGUAGES:
                    jinja_env.globals["GLOBAL_LANGUAGE"] = language
                    with open("{}/{}_{}.tex".format(args.output_folder, regl.filename, language), "w", encoding="utf-8") as f:
                        f.write(regl_template.render(
                            regl=regl, asset_path=args.asset_path))

        case "csv":
            rsvss = bylaws.parse(args.input)
            rsvss.numbering_pass()
            csv_template = jinja_env.get_template("regulation.csv.j2")

            if isinstance(rsvss, bylaws.Bylaws):
                for regl in rsvss.regulations:
                    with open("{}/{}.csv".format(args.output_folder, regl.filename), "w", encoding="utf-8") as f:
                        f.write(csv_template.render(regl=regl))
            else:
                regl = rsvss
                with open("{}/{}.csv".format(args.output_folder, regl.filename), "w", encoding="utf-8") as f:
                    f.write(csv_template.render(regl=regl))

        case "navbar":
            navbar_template = jinja_env.get_template("navbar.html.j2")
            with urllib.request.urlopen("https://static.vseth.ethz.ch/assets/vseth-0100-verband/config.json") as response:
                externalNavbarData = json.loads(response.read())
                with open("{}/header.hbs".format(args.output_folder), "w", encoding="utf-8") as f:
                    f.write(navbar_template.render(
                        primaryNavBarData=externalNavbarData))
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
    (re.compile(r'\.\.\.+'), r'\\ldots')
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
        raise ValueError(
            "cannot convert numbers larger than 14 to latin numeral (if you see this, the Rechtssammlung is in big trouble...)")

    return ["", "bis", "ter", "quarter", "quinquies", "sexies", "septies", "octies", "novies", "decies", "undecies", "duodecies", "terdecies", "quaterdecies"][counter]

# Filter to convert pyhton date objects to dd.mm.YYYY strings.


def format_date(date: date):
    return date.strftime("%d.%m.%Y")


def insert_minutes(args):
    print("Inserting minutes for {} on {} into the Rechtssammlung".format(
        args.gremium, args.date))

    xml_files = []
    for file in os.listdir("."):
        if file.endswith(".xml"):
            xml_files.append(file)

    for xml_file in xml_files:
        with open(xml_file, "r", encoding="utf-8") as f:
            xml = f.read()
            # Add the minutes link to all change footnotes for the given gremium and date.
            # Update the link if it already exists.
            xml, count = re.subn(
                r'<(inserted|deleted|changed)(.*gremium="{}")(.*meeting_date="{}")(.*minutes_link="[^"]*")?(.*[^>]*)?>'.format(
                    args.gremium, args.date),
                r'<\1\2\3 minutes_link="{}"\5>'.format(args.minutes_link), xml)
        with open(xml_file, "w", encoding="utf-8") as f:
            f.write(xml)

        print("Updated {} change footnotes in {}".format(count, xml_file))


if __name__ == "__main__":
    main()
