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

    def bylaws_start(self, element):
        title = element.get("title")
        self.emit_ln('=' * len(title))
        self.emit_ln(title)
        self.emit_ln('=' * len(title))
        self.emit_ln()
        self.emit_ln(".. toctree::")
        self.indent(3)
        self.emit_ln(":maxdepth: 1")
        self.emit_ln()

    def bylaws_end(self, element):
        pass

    def include_start(self, element):
        path = element.get("path")
        path = re.sub(r"\.xml$", "", path)
        self.emit_ln(path)

    def include_end(self, element):
        pass

    def regulation_start(self, element):
        title = element.get("title")
        short = element.get("short")
        if short:
            title = f"{title} ({short})"
        self.emit_ln('=' * len(title))
        self.emit_ln(title)
        self.emit_ln('=' * len(title))
        self.article_counter = 1

    def regulation_end(self, element):
        del self.article_counter

    def section_start(self, element):
        title = element.get("title")
        self.emit_ln()
        self.emit_ln(title)
        self.emit_ln('=' * len(title))

    def section_end(self, element):
        pass

    def subsection_start(self, element):
        title = element.get("title")
        self.emit_ln()
        self.emit_ln(title)
        self.emit_ln('-' * len(title))

    def subsection_end(self, element):
        pass

    def subsubsection_start(self, element):
        title = element.get("title")
        self.emit_ln()
        self.emit_ln(title)
        self.emit_ln('"' * len(title))

    def subsubsection_end(self, element):
        pass

    def articles_start(self, element):
        pass

    def articles_end(self, element):
        pass

    def article_start(self, element):
        title = element.get("title")
        slug = slugify(title)
        text = element.text.strip()
        self.ids.append(slug)
        id = ".".join(self.ids)
        title = f"Art. {self.article_counter} {title}"
        self.emit_ln()
        self.emit_ln(title)
        self.emit_ln('.' * len(title))
        self.emit(text)

    def article_end(self, element):
        self.emit_ln()
        self.ids.pop()
        self.article_counter += 1

    def paragraphs_start(self, element):
        self.emit_ln()
        self.emit_ln()
        self.paragraph_counter = 1

    def paragraphs_end(self, element):
        del self.paragraph_counter
        self.emit_ln()
        self.emit_ln()

    def paragraph_start(self, element):
        text = element.text.strip()
        label = str(self.paragraph_counter)
        self.ids.append(label)
        id = ".".join(self.ids)
        self.emit(f"{label}. {text}")
        self.indent(len(label) + 1)

    def paragraph_end(self, element):
        self.emit_ln()
        self.dedent()
        self.ids.pop()
        self.paragraph_counter += 1

    def letters_start(self, element):
        self.emit_ln()
        self.emit_ln()
        self.letter_counter = 0

    def letters_end(self, element):
        del self.letter_counter
        self.emit_ln()
        self.emit_ln()

    def letter_start(self, element):
        text = element.text.strip()
        label = ascii_lowercase[self.letter_counter]
        self.ids.append(label)
        id = ".".join(self.ids)
        self.emit(f"{label}) {text}")
        self.indent(len(label) + 1)

    def letter_end(self, element):
        self.emit_ln()
        self.dedent()
        self.ids.pop()
        self.letter_counter += 1

    def numerals_start(self, element):
        self.emit_ln()
        self.emit_ln()
        self.numeral_counter = 1

    def numerals_end(self, element):
        del self.numeral_counter
        self.emit_ln()
        self.emit_ln()

    def numeral_start(self, element):
        text = element.text.strip()
        label = toRoman(self.numeral_counter).lower()
        self.ids.append(label)
        id = ".".join(self.ids)
        self.emit(f"{label}) {text}")
        self.indent(len(label) + 1)

    def numeral_end(self, element):
        self.emit_ln()
        self.dedent()
        self.ids.pop()
        self.numeral_counter += 1

    def quote_start(self, element):
        self.result += ' "'
        self.result += element.text.strip()

    def quote_end(self, element):
        self.result += '" '
        if not is_empty(element.tail):
            self.result += element.tail.strip()

    def link_start(self, element):
        # TODO
        pass

    def link_end(self, element):
        # TODO
        pass

    def __str__(self):
        result = re.sub('" ([.,])', r'"\1', self.result)
        result = re.sub('^\s+$', '', result)
        result = re.sub(r'\n\n\n*', '\n\n', result, 0, re.MULTILINE)
        return result
