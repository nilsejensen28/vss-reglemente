#!/usr/bin/env python

class Visitor():
    def bylaws_start(self, element):
        raise NotImplementedError("bylaws_start")

    def bylaws_end(self, element):
        raise NotImplementedError("bylaws_end")

    def include_start(self, element):
        raise NotImplementedError("include_start")

    def include_end(self, element):
        raise NotImplementedError("include_end")

    def regulation_start(self, element):
        raise NotImplementedError("regulation_start")

    def regulation_end(self, element):
        raise NotImplementedError("regulation_end")

    def section_start(self, element):
        raise NotImplementedError("section_start")

    def section_end(self, element):
        raise NotImplementedError("section_end")

    def subsection_start(self, element):
        raise NotImplementedError("subsection_start")

    def subsection_end(self, element):
        raise NotImplementedError("subsection_end")

    def subsubsection_start(self, element):
        raise NotImplementedError("subsubsection_start")

    def subsubsection_end(self, element):
        raise NotImplementedError("subsubsection_end")

    def articles_start(self, element):
        raise NotImplementedError("articles_start")

    def articles_end(self, element):
        raise NotImplementedError("articles_end")

    def article_start(self, element):
        raise NotImplementedError("article_start")

    def article_end(self, element):
        raise NotImplementedError("article_end")

    def paragraphs_start(self, element):
        raise NotImplementedError("paragraphs_start")

    def paragraphs_end(self, element):
        raise NotImplementedError("paragraphs_end")

    def paragraph_start(self, element):
        raise NotImplementedError("paragraph_start")

    def paragraph_end(self, element):
        raise NotImplementedError("paragraph_end")

    def letters_start(self, element):
        raise NotImplementedError("letters_start")

    def letters_end(self, element):
        raise NotImplementedError("letters_end")

    def letter_start(self, element):
        raise NotImplementedError("letter_start")

    def letter_end(self, element):
        raise NotImplementedError("letter_end")

    def numerals_start(self, element):
        raise NotImplementedError("numerals_start")

    def numerals_end(self, element):
        raise NotImplementedError("numerals_end")

    def numeral_start(self, element):
        raise NotImplementedError("numeral_start")

    def numeral_end(self, element):
        raise NotImplementedError("numeral_end")

    def quote_start(self, element):
        raise NotImplementedError("quote_start")

    def quote_end(self, element):
        raise NotImplementedError("quote_end")

    def link_start(self, element):
        raise NotImplementedError("link_start")

    def link_end(self, element):
        raise NotImplementedError("link_end")
