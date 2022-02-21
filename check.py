#!/usr/bin/env python
from visitor import Visitor

class Checker(Visitor):
    def bylaws(self, element):
        assert element.getparent() is None
        assert is_empty(element.text)
        assert is_empty(element.tail)

    def regulation(self, element):
        assert element.getparent() is None or element.getparent().tag == "bylaws"
        assert not is_empty(element.get("title"))
        assert is_empty(element.text)
        assert is_empty(element.tail)

    def preamble(self, element):
        assert element.getparent().tag == "regulation"
        assert is_empty(element.tail)

    def section(self, element):
        assert element.getparent().tag == "regulation"
        assert not is_empty(element.get("title"))
        assert is_empty(element.text)
        assert is_empty(element.tail)

    def subsection(self, element):
        assert element.getparent().tag == "section"
        assert not is_empty(element.get("title"))
        assert is_empty(element.text)
        assert is_empty(element.tail)

    def subsubsection(self, element):
        assert element.getparent().tag == "subsection"
        assert not is_empty(element.get("title"))
        assert is_empty(element.text)
        assert is_empty(element.tail)

    def articles(self, element):
        assert element.getparent().tag in ["regulation", "section", "subsection", "subsubsection"]
        assert is_empty(element.text)
        assert is_empty(element.tail)

    def article(self, element):
        assert element.getparent().tag == "articles"
        assert not is_empty(element.get("title"))
        assert is_empty(element.tail)

    def paragraphs(self, element):
        assert element.getparent().tag == "article"
        assert is_empty(element.text)
        assert is_empty(element.tail)

    def paragraph(self, element):
        assert element.getparent().tag == "paragraphs"
        assert is_empty(element.tail)

    def letters(self, element):
        assert element.getparent().tag in ["article", "paragraph"]
        assert is_empty(element.text)
        assert is_empty(element.tail)

    def letter(self, element):
        assert element.getparent().tag == "letters"
        assert is_empty(element.tail)

    def numerals(self, element):
        assert element.getparent().tag == "letter"
        assert is_empty(element.text)
        assert is_empty(element.tail)

    def numeral(self, element):
        assert element.getparent().tag == "numerals"
        assert is_empty(element.tail)

    def quote(self, element):
        pass

    def link(self, element):
        assert not is_empty(element.get("to"))


def is_empty(s):
    return s is None or s.strip() == ''
