#!/usr/bin/env python
from visitor import Visitor
from check import is_empty
import re
from slugify import slugify
from string import ascii_lowercase

class HtmlEmitter(Visitor):
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
        self.emit_ln("<html>")
        self.indent()
        self.emit_ln('<head>')
        self.indent()
        self.emit_ln('<meta charset="utf-8" />')
        self.emit_ln(f'<title>{title}</title>')
        self.emit_ln('<link rel="preconnect" href="https://fonts.gstatic.com" />')
        self.emit_ln('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro&display=swap" />')
        self.emit_ln('<link rel="stylesheet" href="style.css" />')
        self.emit_ln('<script src="https://unpkg.com/lunr/lunr.js"></script>')
        self.dedent()
        self.emit_ln('</head>')
        self.emit_ln('<body>')
        self.indent()

    def footer(self):
        self.emit_ln('<script type="module">')
        self.indent()
        self.emit_ln('"use strict";')
        self.emit_ln(r'const filename = location.href.replace(/^(.*\/)?([^\/]*)\.html$/, "$2.json");')
        self.emit_ln('const documents = await fetch(filename).then(response => { return response.json(); });')
        self.emit_ln('const idx = lunr(function() {')
        self.indent()
        self.emit_ln('this.ref("id");')
        self.emit_ln('this.field("text");')
        self.emit_ln('this.field("title");')
        self.emit_ln('documents.forEach(function(doc) {')
        self.indent()
        self.emit_ln('this.add(doc);')
        self.dedent()
        self.emit_ln('}, this);')
        self.dedent()
        self.emit_ln('});')
        self.emit_ln('window.search = function(term) {')
        self.indent()
        self.emit_ln('return idx.search(term).map(item => {return documents.find(document => item.ref == document.id)});')
        self.dedent()
        self.emit_ln('};')
        self.dedent()
        self.emit_ln('</script>')
        self.dedent()
        self.emit_ln('</body>')
        self.dedent()
        self.emit_ln('</html>')

    def bylaws_start(self, element):
        title = element.get("title")
        self.header(title)
        self.emit_ln('<ul>')
        self.indent()

    def bylaws_end(self, element):
        self.dedent()
        self.emit_ln('</ul>')
        self.dedent()
        self.emit_ln('</body>')
        self.dedent()
        self.emit_ln('</html>')

    def include_start(self, element):
        path = element.get("path")
        path = re.sub(r"\.xml$", ".html", path)
        self.emit_ln(f'<li><a href="{path}">{path}</a></li>')

    def include_end(self, element):
        pass

    def regulation_start(self, element):
        title = element.get("title")
        short = element.get("short")
        if short:
            title = f"{title} ({short})"
        self.header(title)
        self.emit_ln(f'<h1>{title}</h1>')

    def regulation_end(self, element):
        self.footer()

    def section_start(self, element):
        title = element.get("title")
        self.emit_ln('<section>')
        self.indent()
        self.emit_ln(f'<h2>{title}</h2>')

    def section_end(self, element):
        self.dedent()
        self.emit_ln('</section>')

    def subsection_start(self, element):
        title = element.get("title")
        self.emit_ln('<section>')
        self.indent()
        self.emit_ln(f'<h3>{title}</h3>')

    def subsection_end(self, element):
        self.dedent()
        self.emit_ln('</section>')

    def subsubsection_start(self, element):
        title = element.get("title")
        self.emit_ln('<section>')
        self.indent()
        self.emit_ln(f'<h4>{title}</h4>')

    def subsubsection_end(self, element):
        self.dedent()
        self.emit_ln('</section>')

    def articles_start(self, element):
        pass

    def articles_end(self, element):
        pass

    def article_start(self, element):
        title = element.get("title")
        slug = slugify(title)
        self.ids.append(slug)
        id = ".".join(self.ids)
        self.emit_ln(f'<h5 id="{id}">{title}</h5>')
        self.emit_ln(element.text.strip())

    def article_end(self, element):
        self.ids.pop()

    def paragraphs_start(self, element):
        self.emit_ln('<ol class="paragraphs">')
        self.indent()
        self.paragraph_counter = 1

    def paragraphs_end(self, element):
        del self.paragraph_counter
        self.dedent()
        self.emit_ln('</ol>')

    def paragraph_start(self, element):
        text = element.text.strip()
        self.ids.append(str(self.paragraph_counter))
        id = ".".join(self.ids)
        self.emit_ln(f'<li id="{id}">{text}')

    def paragraph_end(self, element):
        self.emit_ln('</li>')
        self.ids.pop()
        self.paragraph_counter += 1

    def letters_start(self, element):
        self.emit_ln('<ol class="letters">')
        self.indent()
        self.letter_counter = 0

    def letters_end(self, element):
        del self.letter_counter
        self.dedent()
        self.emit_ln('</ol>')

    def letter_start(self, element):
        text = element.text.strip()
        self.ids.append(ascii_lowercase[self.letter_counter])
        id = ".".join(self.ids)
        self.emit_ln(f'<li id="{id}">{text}')

    def letter_end(self, element):
        self.emit_ln('</li>')
        self.ids.pop()
        self.letter_counter += 1

    def numerals_start(self, element):
        self.emit_ln('<ol class="numerals">')
        self.indent()
        self.numeral_counter = 1

    def numerals_end(self, element):
        del self.numeral_counter
        self.dedent()
        self.emit_ln('</li>')

    def numeral_start(self, element):
        text = element.text.strip()
        self.ids.append(str(self.numeral_counter))
        id = ".".join(self.ids)
        self.emit_ln(f'<li id="{id}">{text}')

    def numeral_end(self, element):
        self.emit_ln('</li>')
        self.ids.pop()
        self.numeral_counter += 1

    def quote_start(self, element):
        self.result += ' <q>'
        self.result += element.text.strip()

    def quote_end(self, element):
        self.result += '</q> '
        if not is_empty(element.tail):
            self.result += element.tail.strip()

    def link_start(self, element):
        to = element.get("to")
        self.result += f' <a href="{to}">'
        self.result += element.text.strip()

    def link_end(self, element):
        self.result += '</a> '
        if not is_empty(element.tail):
            self.result += element.tail.strip()

    def __str__(self):
        result = re.sub('</q> ([.,])', r'</q>\1', self.result)
        result = re.sub('</a> ([.,])', r'</a>\1', result)
        return result
