#!/usr/bin/env python
from visitor import Visitor
from slugify import slugify
from string import ascii_lowercase
from check import is_empty

class LatexEmitter(Visitor):
    def __init__(self):
        self.result = ""
        self.indent_level = 0
        self.ids = []

    def emit(self, s):
        self.result += '\t' * self.indent_level
        self.result += s

    def emit_ln(self, s):
        self.emit(s + '\n')

    def indent(self):
        self.indent_level += 1

    def dedent(self):
        self.indent_level -= 1
        assert self.indent_level >= 0

    def header(self, title):
        self.emit_ln(r"\documentclass{scrartcl}")
        self.emit_ln(r"\usepackage{fontspec}")
        self.emit_ln(r"\setmainfont{Source Sans Pro}")
        self.emit_ln(r"\setsansfont{Source Sans Pro}")
        self.emit_ln(r"\usepackage{csquotes}")
        self.emit_ln(r"\usepackage{hyperref}")
        self.emit_ln(r"\usepackage{enumitem}")
        self.emit_ln(r"\title{" + title + "}")
        self.emit_ln(r"\begin{document}")
        self.indent()
        self.emit_ln(r"\maketitle")

    def footer(self):
        self.dedent()
        self.emit_ln(r"\end{document}")
        self.emit_ln(r"\endinput")

    def bylaws_start(self, element):
        title = element.get("title")
        self.header(title)

    def bylaws_end(self, element):
        self.footer()

    def include_start(self, element):
        pass

    def include_end(self, element):
        pass

    def regulation_start(self, element):
        title = element.get("title")
        short = element.get("short")
        if short:
            title = f"{title} ({short})"
        self.header(title)
        self.article_counter = 1

    def regulation_end(self, element):
        self.footer()

    def section_start(self, element):
        title = element.get("title")
        self.emit_ln(r"\section{" + title + "}")

    def section_end(self, element):
        pass

    def subsection_start(self, element):
        title = element.get("title")
        self.emit_ln(r"\subsection{" + title + "}")

    def subsection_end(self, element):
        pass

    def subsubsection_start(self, element):
        title = element.get("title")
        self.emit_ln(r"\subsubsection{" + title + "}")

    def subsubsection_end(self, element):
        pass

    def articles_start(self, element):
        pass

    def articles_end(self, element):
        pass

    def article_start(self, element):
        title = element.get("title")
        slug = slugify(title)
        self.ids.append(slug)
        id = ".".join(self.ids)
        self.emit_ln(r"\par")
        self.emit_ln(r"\textbf{Art.\ " + str(self.article_counter) + ". " + title + "}")
        self.emit_ln(r"\label{" + id + "}")
        self.emit_ln(r"\\")
        self.emit_ln(element.text.strip())

    def article_end(self, element):
        self.ids.pop()
        self.article_counter += 1

    def paragraphs_start(self, element):
        self.emit_ln(r"\begin{enumerate}[label=\textsuperscript{\arabic*}]")
        self.indent()
        self.paragraph_counter = 1

    def paragraphs_end(self, element):
        del self.paragraph_counter
        self.dedent()
        self.emit_ln(r"\end{enumerate}")

    def paragraph_start(self, element):
        text = element.text.strip()
        self.ids.append(str(self.paragraph_counter))
        self.emit_ln(r"\item " + text)

    def paragraph_end(self, element):
        self.ids.pop()
        self.paragraph_counter += 1

    def letters_start(self, element):
        self.emit_ln(r"\begin{enumerate}[label=\alph*)]")
        self.indent()
        self.letter_counter = 0

    def letters_end(self, element):
        del self.letter_counter
        self.dedent()
        self.emit_ln(r"\end{enumerate}")

    def letter_start(self, element):
        text = element.text.strip()
        self.ids.append(ascii_lowercase[self.letter_counter])
        id = ".".join(self.ids)
        self.emit_ln(r"\item " + text)

    def letter_end(self, element):
        self.ids.pop()
        self.letter_counter += 1

    def numerals_start(self, element):
        self.emit_ln(r"\begin{enumerate}[label=\roman*.]")
        self.indent()
        self.numeral_counter = 1

    def numerals_end(self, element):
        del self.numeral_counter
        self.dedent()
        self.emit_ln(r"\end{enumerate}")

    def numeral_start(self, element):
        text = element.text.strip()
        self.ids.append(str(self.numeral_counter))
        id = ".".join(self.ids)
        self.emit_ln(r"\item " + text)

    def numeral_end(self, element):
        self.ids.pop()
        self.numeral_counter += 1

    def quote_start(self, element):
        text = element.text.strip()
        self.result += r" \enquote{"
        self.result += text

    def quote_end(self, element):
        self.result += "} "
        if not is_empty(element.tail):
            self.result += element.tail.strip()

    def link_start(self, element):
        pass

    def link_end(self, element):
        pass

    def __str__(self):
        # TODO
        return self.result

