#!/usr/bin/env python
from visitor import Visitor
from string import ascii_lowercase
from roman import toRoman
import json
from check import is_empty

class JsonEmitter(Visitor):
    def __init__(self):
        self.documents = []
        self.ids = []

    def emit(self, document):
        self.documents.append(document)

    def bylaws(self, element):
        for child in element:
            self.dispatch(child)

    def regulation(self, element):
        title = element.get("title")
        short = element.get("short")
        if short:
            title = f"{title} ({short})"
        id = element.get("id")
        self.ids.append(id)
        self.emit({"id": id, "title": title, "type": "regulation"})
        self.article_counter = 1
        self.section_counter = 1

        for child in element:
            self.dispatch(child)

        del self.section_counter
        del self.article_counter
        self.ids.pop()

    def preamble(self, element):
        text = element.text.strip()
        self.emit({"type": "preamble", "text": text})

        # TODO

    def section(self, element):
        title = element.get("title")
        self.ids.append(str(self.section_counter))
        id = self.ids[0] + "/" + ".".join(self.ids[1:])
        self.emit({"id": id, "title": title, "type": "section"})
        self.subsection_counter = 1

        for child in element:
            self.dispatch(child)

        self.section_counter += 1
        del self.subsection_counter
        self.ids.pop()

    def subsection(self, element):
        title = element.get("title")
        self.ids.append(str(self.subsection_counter))
        id = self.ids[0] + "/" + ".".join(self.ids[1:])
        self.emit({"id": id, "title": title, "type": "subsection"})
        self.subsubsection_counter = 1

        for child in element:
            self.dispatch(child)

        self.subsection_counter + 1
        del self.subsubsection_counter
        self.ids.pop()

    def subsubsection(self, element):
        title = element.get("title")
        self.ids.append(str(self.subsubsection_counter))
        id = self.ids[0] + "/" + ".".join(self.ids[1:])
        self.emit({"id": id, "title": title, "type": "subsubsection"})

        for child in element:
            self.dispatch(child)

        self.subsubsection_counter += 1
        self.ids.pop()

    def articles(self, element):
        for child in element:
            self.dispatch(child)

    def article(self, element):
        if not is_empty(element.text):
            title = element.get("title")
            text = element.text.strip()
            self.ids.append(str(self.article_counter))
            id = self.ids[0] + "/" + ".".join(self.ids[1:])
            self.emit({"id": id, "title": title, "text": text, "type": "article"})

        for child in element:
            self.dispatch(child)

        self.article_counter += 1
        if not is_empty(element.text):
            self.ids.pop()

    def paragraphs(self, element):
        self.paragraph_counter = 1

        for child in element:
            self.dispatch(child)

        del self.paragraph_counter

    def paragraph(self, element):
        text = element.text.strip()
        self.ids.append(str(self.paragraph_counter))
        id = self.ids[0] + "/" + ".".join(self.ids[1:])
        self.emit({"id": id, "text": text, "type": "paragraph"})

        for child in element:
            self.dispatch(child)

        self.paragraph_counter += 1
        self.ids.pop()

    def letters(self, element):
        self.letter_counter = 0

        for child in element:
            self.dispatch(child)

        del self.letter_counter

    def letter(self, element):
        text = element.text.strip()
        self.ids.append(ascii_lowercase[self.letter_counter])
        id = self.ids[0] + "/" + ".".join(self.ids[1:])
        self.emit({"id": id, "text": text, "type": "letter"})

        for child in element:
            self.dispatch(child)

        self.letter_counter += 1
        self.ids.pop()

    def numerals(self, element):
        self.numeral_counter = 1

        for child in element:
            self.dispatch(child)

        del self.numeral_counter

    def numeral(self, element):
        text = element.text.strip()
        self.ids.append(toRoman(self.numeral_counter).lower())
        id = self.ids[0] + "/" + ".".join(self.ids[1:])
        self.emit({"id": id, "text": text, "type": "numeral"})

        for child in element:
            self.dispatch(child)

        self.numeral_counter += 1
        self.ids.pop()

    def quote(self, element):
        # TODO
        for child in element:
            self.dispatch(child)

    def link(self, element):
        # TODO
        for child in element:
            self.dispatch(child)

    def comment(self, element):
        # TODO
        pass

    def __str__(self):
        return json.dumps(self.documents, ensure_ascii=False, indent='\t')
