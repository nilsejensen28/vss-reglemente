#!/usr/bin/env python
from visitor import Visitor

class Checker(Visitor):
    def bylaws_start(self, element):
        assert is_empty(element.text)

    def bylaws_end(self, element):
        assert is_empty(element.tail)

    def include_start(self, element):
        assert element.getparent().tag == "bylaws"
        assert is_empty(element.text)

    def include_end(self, element):
        assert is_empty(element.tail)

    def regulation_start(self, element):
        assert not is_empty(element.get("title"))
        assert is_empty(element.text)

    def regulation_end(self, element):
        assert is_empty(element.tail)

    def section_start(self, element):
        assert element.getparent().tag == "regulation"
        assert not is_empty(element.get("title"))
        assert is_empty(element.text)

    def section_end(self, element):
        assert is_empty(element.tail)

    def subsection_start(self, element):
        assert element.getparent().tag == "section"
        assert not is_empty(element.get("title"))
        assert is_empty(element.text)

    def subsection_end(self, element):
        assert is_empty(element.tail)

    def subsubsection_start(self, element):
        assert element.getparent().tag == "subsection"
        assert not is_empty(element.get("title"))
        assert is_empty(element.text)

    def subsubsection_end(self, element):
        assert is_empty(element.tail)

    def articles_start(self, element):
        assert element.getparent().tag in ["regulation", "section", "subsection", "subsubsection"]
        assert is_empty(element.text)

    def articles_end(self, element):
        assert is_empty(element.tail)

    def article_start(self, element):
        assert element.getparent().tag == "articles"
        assert not is_empty(element.get("title"))

    def article_end(self, element):
        assert is_empty(element.tail)

    def paragraphs_start(self, element):
        assert element.getparent().tag == "article"
        assert is_empty(element.text)

    def paragraphs_end(self, element):
        assert is_empty(element.tail)

    def paragraph_start(self, element):
        assert element.getparent().tag == "paragraphs"

    def paragraph_end(self, element):
        assert is_empty(element.tail)

    def letters_start(self, element):
        assert element.getparent().tag in ["article", "paragraph"]
        assert is_empty(element.text)

    def letters_end(self, element):
        assert is_empty(element.tail)

    def letter_start(self, element):
        assert element.getparent().tag == "letters"

    def letter_end(self, element):
        assert is_empty(element.tail)

    def numerals_start(self, element):
        assert element.getparent().tag == "letter"
        assert is_empty(element.text)

    def numerals_end(self, element):
        assert is_empty(element.tail)

    def numeral_start(self, element):
        assert element.getparent().tag == "numerals"

    def numeral_end(self, element):
        assert is_empty(element.tail)

    def quote_start(self, element):
        pass

    def quote_end(self, element):
        pass

    def link_start(self, element):
        assert not is_empty(element.get("to"))

    def link_end(self, element):
        pass


def is_empty(s):
    return s is None or s.strip() == ''
