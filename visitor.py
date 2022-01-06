#!/usr/bin/env python
from lxml import etree

class Visitor():
    def process(self, input_filename):
        self.input_filename = input_filename
        parser = etree.XMLParser(remove_comments=True)
        tree = etree.parse(input_filename, parser)
        self.dispatch(tree.getroot())

        return self

    def dispatch(self, element):
        try:
            match element.tag:
                case "bylaws":
                    self.bylaws(element)
                case "include":
                    self.include(element)
                case "regulation":
                    self.regulation(element)
                case "section":
                    self.section(element)
                case "subsection":
                    self.subsection(element)
                case "subsubsection":
                    self.subsubsection(element)
                case "articles":
                    self.articles(element)
                case "article":
                    self.article(element)
                case "paragraphs":
                    self.paragraphs(element)
                case "paragraph":
                    self.paragraph(element)
                case "letters":
                    self.letters(element)
                case "letter":
                    self.letter(element)
                case "numerals":
                    self.numerals(element)
                case "numeral":
                    self.numeral(element)
                case "quote":
                    self.quote(element)
                case "link":
                    self.link(element)
                case _:
                    raise RuntimeWarning(f"Unhandled element <{element.tag}>")
        except Exception as e:
            message = ""
            parent = element
            while parent is not None:
                attr = " ".join([f'{k}="{v}"' for k, v in parent.attrib.items()])
                tag = parent.tag
                if attr:
                    tag += " " + attr
                message = f"{self.input_filename}:{parent.sourceline}: in <{tag}>\n" + message
                parent = parent.getparent()

            raise

    def bylaws(self, element):
        raise NotImplementedError("bylaws")

    def include(self, element):
        raise NotImplementedError("include")

    def regulation(self, element):
        raise NotImplementedError("regulation")

    def section(self, element):
        raise NotImplementedError("section")

    def subsection(self, element):
        raise NotImplementedError("subsection")

    def subsubsection(self, element):
        raise NotImplementedError("subsubsection")

    def articles(self, element):
        raise NotImplementedError("articles")

    def article(self, element):
        raise NotImplementedError("article")

    def paragraphs(self, element):
        raise NotImplementedError("paragraphs")

    def paragraph(self, element):
        raise NotImplementedError("paragraph")

    def letters(self, element):
        raise NotImplementedError("letters")

    def letter(self, element):
        raise NotImplementedError("letter")

    def numerals(self, element):
        raise NotImplementedError("numerals")

    def numeral(self, element):
        raise NotImplementedError("numeral")

    def quote(self, element):
        raise NotImplementedError("quote")

    def link(self, element):
        raise NotImplementedError("link")

    def bylaws(self, element):
        raise NotImplementedError("bylaws")

    def include(self, element):
        raise NotImplementedError("include")

    def regulation(self, element):
        raise NotImplementedError("regulation")

    def section(self, element):
        raise NotImplementedError("section")

    def subsection(self, element):
        raise NotImplementedError("subsection")

    def subsubsection(self, element):
        raise NotImplementedError("subsubsection")

    def articles(self, element):
        raise NotImplementedError("articles")

    def article(self, element):
        raise NotImplementedError("article")

    def paragraphs(self, element):
        raise NotImplementedError("paragraphs")

    def paragraph(self, element):
        raise NotImplementedError("paragraph")

    def letters(self, element):
        raise NotImplementedError("letters")

    def letter(self, element):
        raise NotImplementedError("letter")

    def numerals(self, element):
        raise NotImplementedError("numerals")

    def numeral(self, element):
        raise NotImplementedError("numeral")

    def quote(self, element):
        raise NotImplementedError("quote")

    def link(self, element):
        raise NotImplementedError("link")
