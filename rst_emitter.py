#!/usr/bin/env python
from visitor import Visitor
from check import is_empty
import re
from slugify import slugify
from string import ascii_lowercase
from roman import toRoman

class RstEmitter(Visitor):
    def __init__(self):
        self.result = ""
        self.indents = []
        self.ids = []

    def emit(self, s):
        self.result += ''.join([' ' * indent for indent in self.indents])
        self.result += s

    def emit_ln(self, s=''):
        if s == '':
            self.result += '\n'
        else:
            self.emit(s + '\n')

    def indent(self, indent):
        assert indent > 0
        self.indents.append(indent)

    def dedent(self):
        self.indents.pop()

    def bylaws(self, element):
        title = element.get("title")
        self.emit_ln('=' * len(title))
        self.emit_ln(title)
        self.emit_ln('=' * len(title))
        self.emit_ln()
        self.emit_ln(".. toctree::")
        self.indent(3)
        self.emit_ln(":maxdepth: 1")
        self.emit_ln()

        for child in element:
            self.dispatch(child)

    def regulation(self, element):
        if element.getparent() is None:
            title = element.get("title")
            short = element.get("short")
            if short:
                title = f"{title} ({short})"
            self.emit_ln('=' * len(title))
            self.emit_ln(title)
            self.emit_ln('=' * len(title))
            self.article_counter = 1

            for child in element:
                self.dispatch(child)

            del self.article_counter
        else:
            base = re.sub(r"\.xml$", "", element.base)
            self.emit_ln(base)

    def section(self, element):
        title = element.get("title")
        self.emit_ln()
        self.emit_ln(title)
        self.emit_ln('=' * len(title))

        for child in element:
            self.dispatch(child)

    def subsection(self, element):
        title = element.get("title")
        self.emit_ln()
        self.emit_ln(title)
        self.emit_ln('-' * len(title))

        for child in element:
            self.dispatch(child)

    def subsubsection(self, element):
        title = element.get("title")
        self.emit_ln()
        self.emit_ln(title)
        self.emit_ln('"' * len(title))

        for child in element:
            self.dispatch(child)

    def articles(self, element):
        for child in element:
            self.dispatch(child)

    def article(self, element):
        title = element.get("title")
        slug = slugify(title)
        self.ids.append(slug)
        id = ".".join(self.ids)
        title = f"Art. {self.article_counter} {title}"
        self.emit_ln()
        self.emit_ln(title)
        self.emit_ln('.' * len(title))
        if not is_empty(element.text):
            self.emit(element.text.strip())

        for child in element:
            self.dispatch(child)

        self.emit_ln()
        self.ids.pop()
        self.article_counter += 1

    def paragraphs(self, element):
        self.emit_ln()
        self.emit_ln()
        self.paragraph_counter = 1

        for child in element:
            self.dispatch(child)

        del self.paragraph_counter
        self.emit_ln()
        self.emit_ln()

    def paragraph(self, element):
        text = element.text.strip()
        label = str(self.paragraph_counter)
        self.ids.append(label)
        id = ".".join(self.ids)
        self.emit(f"{label}. {text}")
        self.indent(len(label) + 1)

        for child in element:
            self.dispatch(child)

        self.emit_ln()
        self.dedent()
        self.ids.pop()
        self.paragraph_counter += 1

    def letters(self, element):
        self.emit_ln()
        self.emit_ln()
        self.letter_counter = 0

        for child in element:
            self.dispatch(child)

        del self.letter_counter
        self.emit_ln()
        self.emit_ln()

    def letter(self, element):
        text = element.text.strip()
        label = ascii_lowercase[self.letter_counter]
        self.ids.append(label)
        id = ".".join(self.ids)
        self.emit(f"{label}) {text}")
        self.indent(len(label) + 1)

        for child in element:
            self.dispatch(child)

        self.emit_ln()
        self.dedent()
        self.ids.pop()
        self.letter_counter += 1

    def numerals(self, element):
        self.emit_ln()
        self.emit_ln()
        self.numeral_counter = 1

        for child in element:
            self.dispatch(child)

        del self.numeral_counter
        self.emit_ln()
        self.emit_ln()

    def numeral(self, element):
        text = element.text.strip()
        label = toRoman(self.numeral_counter).lower()
        self.ids.append(label)
        id = ".".join(self.ids)
        self.emit(f"{label}) {text}")
        self.indent(len(label) + 1)

        for child in element:
            self.dispatch(child)

        self.emit_ln()
        self.dedent()
        self.ids.pop()
        self.numeral_counter += 1

    def quote(self, element):
        self.result += ' "'
        self.result += element.text.strip()

        for child in element:
            self.dispatch(child)

        self.result += '" '
        if not is_empty(element.tail):
            self.result += element.tail.strip()

    def link(self, element):
        # TODO
        for child in element:
            self.dispatch(child)

    def __str__(self):
        result = re.sub('" ([.,])', r'"\1', self.result)
        result = re.sub('^\s+$', '', result)
        result = re.sub(r'\n\n\n*', '\n\n', result, 0, re.MULTILINE)
        return result
