#!/usr/bin/env python
from lxml import etree

class Dispatcher():
    def __init__(self, delegate):
        self.delegate = delegate

    def process(self, input_filename):
        for event, element in etree.iterparse(input_filename, events=("start", "end")):
            try:
                match element.tag, event:
                    case "bylaws", "start":
                        self.delegate.bylaws_start(element)
                    case "bylaws", "end":
                        self.delegate.bylaws_end(element)
                    case "include", "start":
                        self.delegate.include_start(element)
                    case "include", "end":
                        self.delegate.include_end(element)
                    case "regulation", "start":
                        self.delegate.regulation_start(element)
                    case "regulation", "end":
                        self.delegate.regulation_end(element)
                    case "section", "start":
                        self.delegate.section_start(element)
                    case "section", "end":
                        self.delegate.section_end(element)
                    case "subsection", "start":
                        self.delegate.subsection_start(element)
                    case "subsection", "end":
                        self.delegate.subsection_end(element)
                    case "subsubsection", "start":
                        self.delegate.subsubsection_start(element)
                    case "subsubsection", "end":
                        self.delegate.subsubsection_end(element)
                    case "articles", "start":
                        self.delegate.articles_start(element)
                    case "articles", "end":
                        self.delegate.articles_end(element)
                    case "article", "start":
                        self.delegate.article_start(element)
                    case "article", "end":
                        self.delegate.article_end(element)
                    case "paragraphs", "start":
                        self.delegate.paragraphs_start(element)
                    case "paragraphs", "end":
                        self.delegate.paragraphs_end(element)
                    case "paragraph", "start":
                        self.delegate.paragraph_start(element)
                    case "paragraph", "end":
                        self.delegate.paragraph_end(element)
                    case "letters", "start":
                        self.delegate.letters_start(element)
                    case "letters", "end":
                        self.delegate.letters_end(element)
                    case "letter", "start":
                        self.delegate.letter_start(element)
                    case "letter", "end":
                        self.delegate.letter_end(element)
                    case "numerals", "start":
                        self.delegate.numerals_start(element)
                    case "numerals", "end":
                        self.delegate.numerals_end(element)
                    case "numeral", "start":
                        self.delegate.numeral_start(element)
                    case "numeral", "end":
                        self.delegate.numeral_end(element)
                    case "quote", "start":
                        self.delegate.quote_start(element)
                    case "quote", "end":
                        self.delegate.quote_end(element)
                    case "link", "start":
                        self.delegate.link_start(element)
                    case "link", "end":
                        self.delegate.link_end(element)
                    case _:
                        raise RuntimeWarning(f"Unhandled event {event} for <{element.tag}>")
            except Exception as e:
                parent = element
                while parent is not None:
                    attr = " ".join([f'{k}="{v}"' for k, v in parent.attrib.items()])
                    tag = parent.tag
                    if attr:
                        tag += " " + attr
                    print(f"{input_filename}:{parent.sourceline}: in <{tag}>")
                    parent = parent.getparent()

                raise



        return self.delegate
