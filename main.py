#! /usr/bin/env python
from lxml import etree
from string import ascii_lowercase
from roman import toRoman
from argparse import ArgumentParser
import re
from slugify import slugify

from check import Checker
from html_emitter import HtmlEmitter
from rst_emitter import RstEmitter
from json_emitter import JsonEmitter
from latex_emitter import LatexEmitter

def main():
    parser = ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-o", "--output")
    parser.add_argument("-f", "--format", default="rst")
    args = parser.parse_args()

    match args.format:
        case "rst":
            result = str(RstEmitter().process(args.input))
        case "md":
            result = to_md(args.input)
        case "html":
            result = str(HtmlEmitter().process(args.input))
        case "json":
            result = str(JsonEmitter().process(args.input))
        case "tex":
            result = str(LatexEmitter().process(args.input))
        case "check":
            Checker().process(args.input)
            result = ""
        case _:
            raise RuntimeWarning

    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
    else:
        print(result)

def to_md(input_filename):
    result = ""
    indents = []
    for event, element in etree.iterparse(input_filename, events=("start", "end")):
        match element.tag, event:
            case "bylaws", "start":
                title = element.get("title")
                result += f"# {title}" + '\n'
                result += "```{toctree}" + '\n'
                assert element.text is None or element.text.strip() == ''
            case "bylaws", "end":
                result += "```"
                assert element.tail is None or element.tail.strip() == ''
            case "include", "start":
                path = element.get("path")
                path = re.sub(r"\.xml$", "", path)
                result += path + '\n'
                assert element.text is None or element.text.strip() == ''
            case "include", "end":
                assert element.tail is None or element.tail.strip() == ''
            case "regulation", "start":
                title = element.get("title")
                short = element.get("short")
                if short:
                    title = f"{title} ({short})"
                result += f"\n# {title}\n"
                assert element.text is None or element.text.strip() == ''
                article_counter = 1
            case "regulation", "end":
                assert element.tail is None or element.tail.strip() == ''
                del article_counter
            case "section", "start":
                title = element.get("title")
                result += f"\n## {title}\n"
                assert element.text is None or element.text.strip() == ''
            case "section", "end":
                assert element.tail is None or element.tail.strip() == ''
            case "subsection", "start":
                title = element.get("title")
                result += f"\n### {title}\n"
                assert element.text is None or element.text.strip() == ''
            case "subsection", "end":
                assert element.tail is None or element.tail.strip() == ''
            case "subsubsection", "start":
                title = element.get("title")
                result += f"\n#### {title}\n"
                assert element.text is None or element.text.strip() == ''
            case "subsubsection", "end":
                assert element.tail is None or element.tail.strip() == ''
            case "articles", "start":
                assert element.text is None or element.text.strip() == ''
            case "articles", "end":
                assert element.tail is None or element.tail.strip() == ''
            case "article", "start":
                title = element.get("title")
                result += f"\n##### Art. {article_counter} {title}\n"
                article_counter += 1
                result += element.text.strip()
            case "article", "end":
                assert element.tail is None or element.tail.strip() == ''
                result += '\n'
            case "paragraphs", "start":
                assert element.text is None or element.text.strip() == ''
                result += "\n\n"
                paragraph_counter = 1
            case "paragraphs", "end":
                assert element.tail is None or element.tail.strip() == ''
                result += "\n\n"
                del paragraph_counter
            case "paragraph", "start":
                text = element.text.strip()
                label = f" {paragraph_counter}."
                result += label + " " + text
                indents.append(' ' * len(label))
            case "paragraph", "end":
                indents.pop()
                if element.tail is not None and element.tail.strip() != '':
                    result += element.tail.strip()
                result += '\n'
                paragraph_counter += 1
            case "letters", "start":
                assert element.text is None or element.text.strip() == ''
                result += "\n\n"
                letter_counter = 0
            case "letters", "end":
                assert element.tail is None or element.tail.strip() == ''
                result += "\n\n"
                del letter_counter
            case "letter", "start":
                text = element.text.strip()
                label = " " + ascii_lowercase[letter_counter] + ")"
                result += ''.join(indents) + label + " " + text
                indents.append(' ' * len(label))
            case "letter", "end":
                indents.pop()
                if element.tail is not None and element.tail.strip() != '':
                    result += ''.join(indents) + element.tail.strip()
                result += '\n'
                letter_counter += 1
            case "numerals", "start":
                assert element.text is None or element.text.strip() == ''
                result += "\n\n"
                numeral_counter = 1
            case "numerals", "end":
                assert element.tail is None or element.tail.strip() == ''
                result += "\n\n"
                del numeral_counter
            case "numeral", "start":
                text = element.text.strip()
                label = toRoman(numeral_counter).lower() + ")"
                result += ''.join(indents) + label + " " + text
                indents.append(' ' * len(label))
            case "numeral", "end":
                indents.pop()
                if element.tail is not None and element.tail.strip() != '':
                    result += ''.join(indents) + element.tail.strip()
                result += '\n'
                numeral_counter += 1
            case "quote", "start":
                result += ' "'
                result += element.text.strip()
            case "quote", "end":
                result += '" '
                if element.tail is not None and element.tail.strip() != '':
                    result += element.tail.strip()
            case _, _:
                raise RuntimeWarning(f"Unhandled event {event} for element {element.tag}")

    result = re.sub('" ([.,])', r'"\1', result)
    result = re.sub(r"\n\n\n*", "\n\n", result, 0, re.MULTILINE)
    return result

if __name__ == "__main__":
    main()
