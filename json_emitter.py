#!/usr/bin/env python
from visitor import Visitor
from string import ascii_lowercase
from roman import toRoman
import json

class JsonEmitter(Visitor):
    def __init__(self):
        self.documents = []
        self.ids = []

    def emit(self, document):
        self.documents.append(document)

    def bylaws_start(self, element):
        pass

    def bylaws_end(self, element):
        pass

    def include_start(self, element):
        pass

    def include_end(self, element):
        pass

    def regulation_start(self, element):
        title = element.get("title")
        short = element.get("short")
        if short:
            title = f"{title} ({short})"
        id = element.get("id")
        self.ids.append(id)
        self.emit({"id": id, "title": title, "type": "regulation"})
        self.article_counter = 1
        self.section_counter = 1

    def regulation_end(self, element):
        del self.section_counter
        del self.article_counter
        self.ids.pop()

    def section_start(self, element):
        title = element.get("title")
        self.ids.append(str(self.section_counter))
        id = self.ids[0] + "/" + ".".join(self.ids[1:])
        self.emit({"id": id, "title": title, "type": "section"})
        self.subsection_counter = 1

    def section_end(self, element):
        self.section_counter += 1
        del self.subsection_counter
        self.ids.pop()

    def subsection_start(self, element):
        title = element.get("title")
        self.ids.append(str(self.subsection_counter))
        id = self.ids[0] + "/" + ".".join(self.ids[1:])
        self.emit({"id": id, "title": title, "type": "subsection"})
        self.subsubsection_counter = 1

    def subsection_end(self, element):
        self.subsection_counter + 1
        del self.subsubsection_counter
        self.ids.pop()

    def subsubsection_start(self, element):
        title = element.get("title")
        self.ids.append(str(self.subsubsection_counter))
        id = self.ids[0] + "/" + ".".join(self.ids[1:])
        self.emit({"id": id, "title": title, "type": "subsubsection"})

    def subsubsection_end(self, element):
        self.subsubsection_counter += 1
        self.ids.pop()

    def articles_start(self, element):
        pass

    def articles_end(self, element):
        pass

    def article_start(self, element):
        title = element.get("title")
        text = element.text.strip()
        self.ids.append(str(self.article_counter))
        id = self.ids[0] + "/" + ".".join(self.ids[1:])
        self.emit({"id": id, "title": title, "text": text, "type": "article"})

    def article_end(self, element):
        self.article_counter += 1
        self.ids.pop()

    def paragraphs_start(self, element):
        self.paragraph_counter = 1

    def paragraphs_end(self, element):
        del self.paragraph_counter

    def paragraph_start(self, element):
        text = element.text.strip()
        self.ids.append(str(self.paragraph_counter))
        id = self.ids[0] + "/" + ".".join(self.ids[1:])
        self.emit({"id": id, "text": text, "type": "paragraph"})

    def paragraph_end(self, element):
        self.paragraph_counter += 1
        self.ids.pop()

    def letters_start(self, element):
        self.letter_counter = 0

    def letters_end(self, element):
        del self.letter_counter

    def letter_start(self, element):
        text = element.text.strip()
        self.ids.append(ascii_lowercase[self.letter_counter])
        id = self.ids[0] + "/" + ".".join(self.ids[1:])
        self.emit({"id": id, "text": text, "type": "letter"})

    def letter_end(self, element):
        self.letter_counter += 1
        self.ids.pop()

    def numerals_start(self, element):
        self.numeral_counter = 1

    def numerals_end(self, element):
        del self.numeral_counter

    def numeral_start(self, element):
        text = element.text.strip()
        self.ids.append(toRoman(self.numeral_counter).lower())
        id = self.ids[0] + "/" + ".".join(self.ids[1:])
        self.emit({"id": id, "text": text, "type": "numeral"})

    def numeral_end(self, element):
        self.numeral_counter += 1
        self.ids.pop()

    def quote_start(self, element):
        # TODO
        pass

    def quote_end(self, element):
        # TODO
        pass

    def linkt_start(self, element):
        # TODO
        pass

    def link_end(self, element):
        # TODO
        pass

    def __str__(self):
        return json.dumps(self.documents, ensure_ascii=False, indent='\t')
