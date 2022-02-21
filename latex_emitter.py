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
        self.emit_ln(r"\documentclass{scrreprt}")
        self.emit_ln(r"\KOMAoptions{chapterentrydots, parskip}")
        self.emit_ln(r"\usepackage{fontspec}")
        self.emit_ln(r"\usepackage{microtype}")
        self.emit_ln(r"\setmainfont{Source Sans Pro}")
        self.emit_ln(r"\setsansfont{Source Sans Pro}")
        self.emit_ln(r"\usepackage{polyglossia}")
        self.emit_ln(r"\setdefaultlanguage[variant=swiss]{german}")
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

    def bylaws(self, element):
        title = element.get("title")
        if element.getparent() is None:
            self.header(title)
            self.emit_ln(r"\tableofcontents")

        for child in element:
            self.dispatch(child)

        if element.getparent() is None:
            self.footer()

    def regulation(self, element):
        title = element.get("title")
        short = element.get("short")
        if short:
            title = f"{title} ({short})"
        if element.getparent() is None:
            self.header(title)
        else:
            self.emit_ln(r"\chapter*{" + title + "}")
            self.emit_ln(r"\addtocentrydefault{chapter}{}{" + title + "}")
            self.emit_ln(r"\stepcounter{chapter}")
        self.article_counter = 1

        for child in element:
            self.dispatch(child)

        if element.getparent() is None:
            self.footer()

    def preamble(self, element):
        text = element.text.strip()
        self.emit(r"\emph{" + text)

        for child in element:
            self.dispatch(child)

        self.emit_ln("}")

    def section(self, element):
        title = element.get("title")
        self.emit_ln(r"\section{" + title + "}")

        for child in element:
            self.dispatch(child)

    def subsection(self, element):
        title = element.get("title")
        self.emit_ln(r"\subsection{" + title + "}")

        for child in element:
            self.dispatch(child)

    def subsubsection(self, element):
        title = element.get("title")
        self.emit_ln(r"\subsubsection{" + title + "}")

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
        self.emit_ln(r"\par")
        self.emit_ln(r"\textbf{Art.\ " + str(self.article_counter) + ". " + title + "}")
        self.emit_ln(r"\label{" + id + "}")
        if not is_empty(element.text):
            self.emit_ln(r"\\")
            self.emit_ln(element.text.strip())

        for child in element:
            self.dispatch(child)

        self.ids.pop()
        self.article_counter += 1

    def paragraphs(self, element):
        self.emit_ln(r"\begin{enumerate}[label=\textsuperscript{\arabic*}, topsep = 0pt, nosep]")
        self.indent()
        self.paragraph_counter = 1

        for child in element:
            self.dispatch(child)

        del self.paragraph_counter
        self.dedent()
        self.emit_ln(r"\end{enumerate}")

    def paragraph(self, element):
        text = element.text.strip()
        self.ids.append(str(self.paragraph_counter))
        self.emit_ln(r"\item " + text)

        for child in element:
            self.dispatch(child)

        self.ids.pop()
        self.paragraph_counter += 1

    def letters(self, element):
        self.emit_ln(r"\begin{enumerate}[label=\alph*), topsep = 0pt, nosep]")
        self.indent()
        self.letter_counter = 0

        for child in element:
            self.dispatch(child)

        del self.letter_counter
        self.dedent()
        self.emit_ln(r"\end{enumerate}")

    def letter(self, element):
        text = element.text.strip()
        self.ids.append(ascii_lowercase[self.letter_counter])
        id = ".".join(self.ids)
        self.emit_ln(r"\item " + text)

        for child in element:
            self.dispatch(child)

        self.ids.pop()
        self.letter_counter += 1

    def numerals(self, element):
        self.emit_ln(r"\begin{enumerate}[label=\roman*., topsep = 0pt, nosep]")
        self.indent()
        self.numeral_counter = 1

        for child in element:
            self.dispatch(child)

        del self.numeral_counter
        self.dedent()
        self.emit_ln(r"\end{enumerate}")

    def numeral(self, element):
        text = element.text.strip()
        self.ids.append(str(self.numeral_counter))
        id = ".".join(self.ids)
        self.emit_ln(r"\item " + text)

        for child in element:
            self.dispatch(child)

        self.ids.pop()
        self.numeral_counter += 1

    def quote(self, element):
        text = element.text.strip()
        self.result += r" \enquote{"
        self.result += text

        for child in element:
            self.dispatch(child)

        if not is_empty(element.tail):
            tail = element.tail.strip()
            if tail[0] in [',', '.', ';']:
                self.result += "}"
            else:
                self.result += "} "
            self.result += element.tail.strip()
        else:
            self.result += "} "

    def link(self, element):
        to = element.get("to")
        text = element.text.strip()
        self.emit(r"\href{" + to + "}{" + text)

        for child in element:
            self.dispatch(child)

        self.emit("}")

        if not is_empty(element.tail):
            self.emit(element.tail.strip())


    def __str__(self):
        return self.result

