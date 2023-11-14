#!/usr/bin/env python
from lxml import etree, ElementInclude
from datetime import date


# Enable including xml documents using xinclude.
# https://stackoverflow.com/a/69618810/6337138
def XinlcudeLoader(href, parse, encoding=None, parser=etree.XMLParser(remove_comments=True)):
    ret = ElementInclude._lxml_default_loader(href, parse, encoding, parser)
    ret.attrib["{http://www.w3.org/XML/1998/namespace}base"] = href
    ret.attrib["filename"] = href
    return ret

# Global counters to track the number of relevant items.
# These counters need to be updated appropriately by the respective classes.
art_counter = 0
inserted_art_counter = 0
abs_counter = 0
inserted_abs_counter = 0
lit_counter = 0
inserted_lit_counter = 0
num_counter = 0
inserted_num_counter = 0
sec_counter = 0
subsec_counter = 0
subsubsec_counter = 0

filename = None


# Custom error function that prints a lot of context helpful when debuging a malformed regulation.
def throw_error(message: str, element: etree.ElementBase):
    print("Error: {}".format(message)) 
    print("element: {}".format(element))
    print("Tag backtrace:")
    parent = element
    location = ""
    while parent is not None:
        tag = parent.tag

        match tag:
            case "article":
                location = "Art. {} {}".format(art_counter, location)
            case "paragraph":
                location = "Abs. {} {}".format(abs_counter, location)
            case "letter":
                location = "lit. {}) {}".format(lit_counter, location)
            case "numeral":
                location = "num. {}) {}".format(num_counter, location)
            case "regulation":
                try:
                    location = "{} {}".format(location, parent.get("title"))
                except Exception:
                    continue

        attr = " ".join([f'{k}="{v}"' for k, v in parent.attrib.items()])
        if attr:
            tag += " " + attr
        print(f"  <{tag}>")

        parent = parent.getparent()

    print("Location: {}".format(location))

    exit(1)


# Parses an XML document to a Bylaws or Regulation object depending on the top level element.
def parse(input_filename):
    tree = etree.parse(input_filename, parser=etree.XMLParser(remove_comments=True))
    global filename
    filename = input_filename
    ElementInclude.include(tree, loader=XinlcudeLoader)
    match tree.getroot().tag:
        case "bylaws":
            return Bylaws(tree.getroot())
        case "regulation":
            return Regulation(tree.getroot())
        case _:
            throw_error("Only bylaws and regulations can be root", tree.getroot())


# Regulation AST
# --------------
#
# All regulation/bylaws components are parsed into objects representing a regulation abstract syntax tree (AST)
# which are then typeset using Jinja templates for different output formats.
#
# During initial parsing each component is initialized with its constructor that takes an `etree.ElementBase`.
# Constructors follow a few steps. First a sanity chech to make sure the element tag is what we expect it to be.
# Then follows a well-formedness check where we make sure that the element contains all values that are expected
# and does not contain any values it should not. Next, the values from the XML element are incorporated into the
# object. The very last step is to iterate over all children of the element and initializing the next objects. In
# case of unexpected children, an error is thrown.
#
# After initial parsing further processing if often needed. We do this with passes over the AST similar to compiler
# passes. Each pass serves a distinct purpose. Passes are basically a fold operation over the entire AST.
# Currently, the following passes are implemented:
#  - collect_footnotes_pass(): Collects footnotes to the component where they are displayed (e.g. articles in case of mdbook)
#  - number_footnotes_pass(): Numbers the footnotes in each component that displays footnotes.

"""
Bylaws: top level object for the collection of all regulations

It is mainly a container object. Only regulations are valid children.

Attributes:
- title: Title of the bylaws
- filename: File name of the XML source containing this element
- regulations: Ordered list of regulations contained in the bylaws
- element: XML element represented by this object
"""
class Bylaws:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "bylaws")
        self.element = element

        # Well-formedness
        if not is_empty(element.text):
            throw_error("Bylaws may not contain text", element)
        if not is_empty(element.tail):
            throw_error("Bylaws may not have a tail (tail: {})".format(element.tail), element)
        if is_empty(element.get("title")):
            throw_error("Bylaws must contain a title", element)
        ensure_inserted_not_present(element)

        # Values
        self.title = element.get("title")
        if is_empty(element.get("filename")):
            self.filename = filename
        else:
            self.filename = element.get("filename")
        self.filename = self.filename.replace(".xml", "")

        self.regulations = []
        for child in element:
            match child.tag:
                case "regulation":
                    self.regulations.append(Regulation(child))
                case _:
                    throw_error("Bylaws only contain regulations", element)


    def collect_footnotes_pass(self):
        for regl in self.regulations:
            regl.collect_footnotes_pass()

    def number_footnotes_pass(self):
        for regl in self.regulations:
            regl.number_footnotes_pass()


"""
Regulation: container for contents of regulations

Valid children: articles, section, preamble

Attributes:
 - title: Full title of the regulations
 - short: Short title of the regulations
 - abbrev: Abbreviation of the regulation title
 - id: RSVSETH id of the regulation
 - is_toplevel: True if the regulation was parsed standalone from its file
 - filename: File name of the XML source for this regulation
 - preamble: Only defined if a preamble is present
 - articles: Ordered list of articles that come before a potential section
 - sections: Ordered list of sections
 - element: XML element represented by this object
"""
class Regulation:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, art_counter, inserted_art_counter, filename

        # Sanity
        assert(element.tag == "regulation")
        self.element = element

        # Well-formedness
        if not is_empty(element.text):
            throw_error("a regulation may not contain text", element)
        if not is_empty(element.tail):
            throw_error("a regulation may not have a tail (tail: {})".format(element.tail), element)
        if is_empty(element.get("title")):
            throw_error("a regulation must have a title", element)
        if is_empty(element.get("id")):
            throw_error("a regulation must contain an id", element)
        ensure_inserted_not_present(element)

        # reset counters
        art_counter, inserted_art_counter, sec_counter = 0, 0, 0

        # Values
        self.title = element.get("title")
        if is_empty(element.get("short")):
            self.short = None
        else:
            self.short = element.get("short")
        if is_empty(element.get("abbrev")):
            self.abbrev = None
        else:
            self.abbrev = element.get("abbrev")
        self.id = element.get("id")
        self.is_toplevel = element.getparent() is not None

        if is_empty(element.get("filename")):
            self.filename = filename
        else:
            self.filename = element.get("filename")
        self.filename = self.filename.replace(".xml", "")

        self.articles = []
        self.sections = []
        for child in element:
            match child.tag:
                case "preamble":
                    self.preamble = Preamble(child)
                case "section":
                    self.sections.append(Section(child))
                case "articles":
                    if len(self.sections) == 0:
                        self.articles = process_articles(child)
                    else:
                        throw_error("a regulation may only contain articles before any sections", element)
                case _:
                    throw_error("a regulation only contain articles, a preamble and sections", element)


    def collect_footnotes_pass(self):
        if hasattr(self, "preamble"):
            self.preamble.collect_footnotes_pass()
        for art in self.articles:
            art.collect_footnotes_pass()
        for sec in self.sections:
            sec.collect_footnotes_pass()

    def number_footnotes_pass(self):
        if hasattr(self, "preamble"):
            self.preamble.number_footnotes_pass()
        
        for art in self.articles:
            art.number_footnotes_pass()

        for sec in self.sections:
            sec.number_footnotes_pass()

"""
Preamble 

Block of text that can have footnotes. Also displays footnotes at the end in mdbook.

Valid children:
 - inserted, changed, deleted: change footnote, at most one
 - link
 - quote
 - footnote

Attributes:
 - footnotes: Ordered list of footnotes as they should be displayed. Filled by collect_footnotes_pass().
 - text: Ordered list of text elements.
 - changeFootnote: a change footnote that is only defined if one is present
 - element: XML element represented by this object
"""
class Preamble:
    def __init__(self, element: etree.ElementBase) -> None:
        # Sanity
        assert(element.tag == "preamble")
        self.element = element

        # Well-formedness
        if not is_empty(element.tail):
            throw_error("a preamble may not have a tail", element)
        ensure_inserted_not_present(element)

        # Values
        self.footnotes = []
        self.text = []
        if not is_empty(element.text):
            self.text.append(element.text)

        for child in element:
            match child:
                case "link":
                    self.text.append(Link(child))
                case "quote":
                    self.text.append(Quote(child))
                case "footnote":
                    self.text.append(Footnote(child))
                case "inserted" | "deleted" | "changed":
                    self.changeFootnote(ChangeFootnote(child))
                    self.text.append(self.changeFootnote)
                case _:
                    throw_error("invalid preamble child <{}>".format(child.tag), element)

    def collect_footnotes_pass(self):
        for elem in self.text:
            if isinstance(elem, Footnote):
                self.footnotes.append(elem)
        
        # Change footnote goes at the end of the preamble.
        if hasattr(self, "changeFootnote"):
            self.footnotes.append(self.changeFootnote)
    
    def number_footnotes_pass(self):
        for i, footnote in enumerate(self.footnotes, 1):
            footnote.number = i


"""
Section

Does not have text. May contain articles before potential subsections. Does not display footnotes.

Valid children: articles, subsection

Attributes:
 - title: section title
 - number: section number
 - articles: ordered list of articles
 - subsections: ordered list of subsections
 - element: XML element represented by this object
"""
class Section:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter
        # Sanity
        assert(element.tag == "section")
        self.element = element

        # Well-formedness
        if not is_empty(element.text):
            throw_error("a section my not contain text on its own", element)
        if not is_empty(element.tail):
            throw_error("a section my not have a tail (tail: {})".format(element.tail), element)
        if is_empty(element.get("title")):
            throw_error("a section must have a title", element)
        ensure_inserted_not_present(element)

        # reset counters
        subsec_counter = 0

        # increment counter
        sec_counter += 1
        

        # values
        self.title = element.get("title")
        self.number = sec_counter
        self.articles = []
        self.subsections = []
        for child in element:
            match child.tag:
                case "articles":
                    if self.subsections == []:
                        self.articles = process_articles(child)
                    else:
                        throw_error("a section my only contain articles before any subsections", element)
                case "subsection":
                    self.subsections.append(Subsection(child))
                case _:
                    throw_error("a section may only cointain articles and subsections", element)

    def collect_footnotes_pass(self):
        for art in self.articles:
            art.collect_footnotes_pass()
        
        for subsec in self.subsections:
            subsec.collect_footnotes_pass()
     
    def number_footnotes_pass(self): 
        for art in self.articles:
            art.number_footnotes_pass()

        for subsec in self.subsections:
            subsec.number_footnotes_pass()


"""
Subsection

Does not have text. May contain articles before potential subsubsections. Does not display footnotes.

Valid children: articles, subsubsection

Attributes:
 - title: subsection title
 - number: subsection number
 - sec: section number of the section that contains this subsection
 - articles: ordered list of articles
 - subsubsections: ordered list of subsubsections
 - element: XML element represented by this object
"""
class Subsection:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter
        # Sanity
        assert(element.tag == "subsection")
        self.element = element

        # Well-formedness
        if not is_empty(element.text):
            throw_error("a subsection my not contain text on its own", element)
        if not is_empty(element.tail):
            throw_error("a subsection my not have a tail (tail: {})".format(element.tail), element)
        if is_empty(element.get("title")):
            throw_error("a subsection must have a title", element)
        ensure_inserted_not_present(element)

        # reset counters
        subsubsec_counter = 0

        # increment counter
        subsec_counter += 1

        # values
        self.title = element.get("title")
        self.sec = sec_counter
        self.number = subsec_counter
        self.articles = []
        self.subsubsections = []
        for child in element:
            match child.tag:
                case "articles":
                    if self.subsubsections == []:
                        self.articles = process_articles(child)
                    else:
                        throw_error("a subsection my only contain articles before any subsections", element)
                case "subsubsection":
                    self.subsubsections.append(Subsubsection(child))
                case _:
                    throw_error("a subsection may only cointain articles and subsubsections", element)

    def collect_footnotes_pass(self):
        for art in self.articles:
            art.collect_footnotes_pass()

        for subsubsec in self.subsubsections:
            subsubsec.collect_footnotes_pass()

    def number_footnotes_pass(self):
        for art in self.articles:
            art.number_footnotes_pass()

        for subsubsec in self.subsubsections:
            subsubsec.number_footnotes_pass()


"""
Subsubection

Does not have text. Contains articles. Does not display footnotes.

Valid children: articles

Attributes:
 - title: subsubsection title
 - number: subsubsection number
 - sec: section number of the section that contains this subsubsection
 - subsec: subsection number of the subsection that contains this subsubsection
 - articles: ordered list of articles
 - element: XML element represented by this object
"""
class Subsubsection:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter
        # Sanity
        assert(element.tag == "subsubsection")
        self.element = element

        # Well-formedness
        if not is_empty(element.text):
            throw_error("a subsubsection my not contain text on its own", element)
        if not is_empty(element.tail):
            throw_error("a subsubsection my not have a tail (tail: {})".format(element.tail), element)
        if is_empty(element.get("title")):
            throw_error("a subsubsection must have a title", element)
        ensure_inserted_not_present(element)

        # increment counter
        subsubsec_counter += 1

        # values
        self.title = element.get("title")
        self.sec = sec_counter
        self.subsec = subsec_counter
        self.number = subsubsec_counter
        self.articles = []
        for child in element:
            match child.tag:
                case "articles":
                    self.articles = process_articles(child)
                case _:
                    throw_error("a subsubsection may only cointain articles", element)

    def collect_footnotes_pass(self):
        for art in self.articles:
            art.collect_footnotes_pass()
    
    def number_footnotes_pass(self):
        for art in self.articles:
            art.number_footnotes_pass()


"""
Article

Can contain text, at most one change footnote, paragraphs, and letters in case the
article does not contain any paragraphs. Displays footnotes in mdbook.

Valid children: 
 - paragraphs, letters, link, quote, footnote
 - inserted, deleted, changed: at most one change footnote 

Attributes:
 - title: article title
 - number: article number
 - inserted_number: number of inserted articles (used for bis, ter numbering)
 - inserted: True iff this article is inserted and gets inserted numbering
 - ended_inserted: True iff the preceding article was inserted and this article is not.
 - text: ordered list of text elements.
 - paragraphs: ordered list of paragraphs
 - letters: ordered list of letters (only if paragraphs is empty)
 - letters_tail: text after letters
 - footnotes: footnotes displayed after this aricle in mdbook
 - changeFootnote: a change footnote that is only defined if one is present
 - element: XML element represented by this object
"""
class Article:
    def __init__(self, element: etree.ElementBase) -> None:
        global art_counter, inserted_art_counter, abs_counter, inserted_abs_counter, lit_counter, inserted_lit_counter
        # Sanity
        assert(element.tag == "article")
        self.element = element

        # well-formedness
        if not is_empty(element.tail):
            throw_error("an article may not have a tail (tail: {})".format(element.tail), element)
        if is_empty(element.get("title")):
            throw_error("an article needs a title", element)
        ensure_inserted_is_empty(element)

        # reset counters
        abs_counter, inserted_abs_counter, lit_counter, inserted_lit_counter = 0, 0, 0, 0

        # increment article counter
        self.ended_inserted = False # is true iff the preceding article was inserted and the current is not
        if element.get("inserted") == "":
            # We have an inserted article. Therefore, we do not increment the normal article counter.
            inserted_art_counter += 1
            self.inserted = True
        else:
            # We have a normal article.
            self.inserted = False
            art_counter += 1
            if inserted_art_counter > 0:
                # This is a normal article and the previous article was inserted. Therefore, reset inserted counter.
                inserted_art_counter = 0
                self.ended_inserted = True

        # values
        self.title = element.get("title")
        self.number = art_counter
        self.inserted_number = inserted_art_counter

        self.text = []
        self.paragraphs = []
        self.letters = []
        self.letters_tail = None
        self.footnotes = []

        if not is_empty(element.text):
            self.text.append(element.text)

        for child in element:
            match child.tag:
                case "paragraphs":
                    if not self.letters == []:
                        throw_error("an article can only have one of paragraphs or letters as direct descendents", element)
                    
                    self.paragraphs = process_paragraphs(child)
                case "letters":
                    if not self.paragraphs == []:
                        throw_error("an article can only have one of paragraphs or letters as direct descendents", element)
                    
                    self.letters, self.letters_tail = process_letters(child)
                case "link":
                    self.text.append(Link(child))
                case "quote":
                    self.text.append(Quote(child))
                case "footnote":
                    self.text.append(Footnote(child))
                case "inserted" | "deleted" | "changed":
                    self.changeFootnote = ChangeFootnote(child)
                    self.text.append(self.changeFootnote)
                case _:
                    throw_error("invalid article child {}".format(child.tag), element)

    def collect_footnotes_pass(self):
        # In articles the change footnote goes after the article number and therefore before any other footnote.
        if hasattr(self, "changeFootnote"):
            self.footnotes.append(self.changeFootnote)

        for elem in self.text:
            if isinstance(elem, Footnote):
                self.footnotes.append(elem)

        for abs in self.paragraphs:
            self.footnotes.extend(abs.collect_footnotes_pass())

        for lit in self.letters:
            self.footnotes.extend(lit.collect_footnotes_pass())

    def number_footnotes_pass(self):
        for i, footnote in enumerate(self.footnotes, 1):
            footnote.number = i


"""
Paragraph

Can contain text, letters, and at most one change footnote. Footnotes are collected to be displayed in article.

Valid children: 
 - letters, link, quote, footnote
 - inserted, deleted, changed: at most one change footnote 

Attributes:
 - number: paragraph number
 - inserted_number: number of inserted paragraph (used for bis, ter numbering)
 - inserted: True iff this paragraph is inserted and gets inserted numbering
 - ended_inserted: True iff the preceding paragraph was inserted and this paragraph is not.
 - text: ordered list of text elements.
 - letters: ordered list of letters (only if paragraphs is empty)
 - letters_tail: text after letters
 - changeFootnote: a change footnote that is only defined if one is present
 - element: XML element represented by this object
"""
class Paragraph:
    def __init__(self, element: etree.ElementBase) -> None:
        global abs_counter, inserted_abs_counter, lit_counter, inserted_lit_counter
        # Sanity
        assert(element.tag == "paragraph")
        self.element = element

        # well-formedness
        if not is_empty(element.tail):
            throw_error("a paragraph may not have a tail (tail: {})".format(element.tail), element)
        ensure_inserted_is_empty(element)

        # reset counters
        lit_counter, inserted_lit_counter = 0, 0

        # increment paragraph number
        self.ended_inserted = False # true iff the preceding paragraph is inserted and the current is not
        if element.get("inserted") == "":
            # We have an inserted paragraph. Therefore, we do not increment the normal paragraph counter.
            inserted_abs_counter += 1
            self.inserted = True
        else:
            # We have a normal paragraph.
            self.inserted = False
            abs_counter += 1
            if inserted_abs_counter > 0:
                # This is a normal paragraph and the previous paragraph was inserted. Therefore, reset inserted counter.
                inserted_abs_counter = 0
                self.ended_inserted = True

        # values
        self.number = abs_counter
        self.inserted_number = inserted_abs_counter

        self.text = []
        self.letters = []
        self.letters_tail = None

        if not is_empty(element.text):
            self.text.append(element.text)

        for child in element:
            match child.tag:
                case "letters":
                    self.letters, self.letters_tail = process_letters(child)
                case "link":
                    self.text.append(Link(child))
                case "quote":
                    self.text.append(Quote(child))
                case "footnote":
                    self.text.append(Footnote(child))
                case "inserted" | "deleted" | "changed":
                    self.changeFootnote = ChangeFootnote(child)
                    self.text.append(self.changeFootnote)
                case _:
                    throw_error("invalid paragraph child <{}>".format(child.tag), element)

    def collect_footnotes_pass(self):
        footnotes = []
        for elem in self.text:
            if isinstance(elem, Footnote):
                footnotes.append(elem)

        # In paragraphs the change footnote goes at the end of the text.
        if hasattr(self, "changeFootnote"):
            footnotes.append(self.changeFootnote)

        for lit in self.letters:
            footnotes.extend(lit.collect_footnotes_pass())
        
        return footnotes


"""
Letter

Can contain text, numerals, and at most one change footnote. Footnotes are collected to be displayed in article.

Valid children: 
 - numerals, link, quote, footnote
 - inserted, deleted, changed: at most one change footnote 

Attributes:
 - number: number to be represented as latin letter
 - inserted_number: number of inserted letter (used for bis, ter numbering)
 - inserted: True iff this letter is inserted and gets inserted numbering
 - ended_inserted: True iff the preceding letter was inserted and this letter is not.
 - text: ordered list of text elements.
 - numerals: ordered list of letters (only if paragraphs is empty)
 - changeFootnote: a change footnote that is only defined if one is present
 - element: XML element represented by this object
"""
class Letter:
    def __init__(self, element: etree.ElementBase) -> None:
        global lit_counter, num_counter, inserted_lit_counter, inserted_num_counter
        # Sanity
        assert(element.tag == "letter")
        self.element = element

        # well-formedness
        if not is_empty(element.tail):
            throw_error("a letter may not have a tail (tail: {})".format(element.tail), element)
        ensure_inserted_is_empty(element)
        
        # reset counter
        num_counter, inserted_num_counter = 0, 0

        # increment letter counter
        self.ended_inserted = False # true if the preceding letter was inserted and the current is not
        if element.get("inserted") == "":
            # We have an inserted letter. Therefore, we do not increment the normal letter counter.
            inserted_lit_counter += 1
            self.inserted = True
        else:
            # We have a normal letter.
            self.inserted = False
            lit_counter += 1
            if inserted_lit_counter > 0:
                # This is a normal letter and the previous letter was inserted. Therefore, reset inserted counter.
                inserted_lit_counter = 0
                self.ended_inserted = True

        # values
        self.number = lit_counter
        self.inserted_number = inserted_lit_counter
        
        self.text = []
        self.numerals = []
        
        if not is_empty(element.text):
            self.text.append(element.text)

        for child in element:
            match child.tag:
                case "numerals":
                    self.numerals = process_numerals(child)
                case "link":
                    self.text.append(Link(child))
                case "quote":
                    self.text.append(Quote(child))
                case "footnote":
                    self.text.append(Footnote(child))
                case "inserted" | "deleted" | "changed":
                    self.changeFootnote = ChangeFootnote(child)
                    self.text.append(self.changeFootnote)
                case _:
                    throw_error("invalid letter child {}".format(child.tag), element)

    def collect_footnotes_pass(self):
        footnotes = []
        for elem in self.text:
            if isinstance(elem, Footnote):
                footnotes.append(elem)

        # The change footnote goes at the end of the text.
        if hasattr(self, "changeFootnote"):
            footnotes.append(self.changeFootnote)

        for num in self.numerals:
            footnotes.extend(num.collect_footnotes_pass())

        return footnotes


"""
Numeral

Can contain text and at most one change footnote. Footnotes are collected to be displayed in article.

Valid children: 
 - link, quote, footnote
 - inserted, deleted, changed: at most one change footnote 

Attributes:
 - number: number of the numeral
 - inserted_number: number of inserted numeral (used for bis, ter numbering)
 - inserted: True iff this numeral is inserted and gets inserted numbering
 - ended_inserted: True iff the preceding numeral was inserted and this numeral is not.
 - text: ordered list of text elements.
 - changeFootnote: a change footnote that is only defined if one is present
 - element: XML element represented by this object
"""
class Numeral:
    def __init__(self, element: etree.ElementBase) -> None:
        global num_counter, inserted_num_counter
        # Sanity
        assert(element.tag == "numeral")
        self.element = element

        # well-formedness
        if not is_empty(element.tail):
            throw_error("a numeral may not have a tail (tail: {})".format(element.tail), element)
        ensure_inserted_is_empty(element)

        # increment numeral counter
        self.ended_inserted = False # true if the preceding numeral is inserted and the current is not
        if element.get("inserted") == "":
            # We have an inserted numeral. Therefore, we do not increment the normal numeral counter.
            inserted_num_counter += 1
            self.inserted = True
        else:
            # We have a normal numeral.
            self.inserted = False
            num_counter += 1
            if inserted_num_counter > 0:
                # This is a normal numeral and the previous numeral was inserted. Therefore, reset inserted counter.
                inserted_num_counter = 0
                self.ended_inserted = True

        # values
        self.number = num_counter
        self.inserted_number = inserted_num_counter

        self.text = []

        if not is_empty(element.text):
            self.text.append(element.text)

        for child in element:
            match child.tag:
                case "link":
                    self.text.append(Link(child))
                case "quote":
                    self.text.append(Quote(child))
                case "footnote":
                    self.text.append(Footnote(child))
                case "inserted" | "deleted" | "changed":
                    self.changeFootnote = ChangeFootnote(child)
                    self.text.append(self.changeFootnote)
                case _:
                    throw_error("invalid numeral child {}".format(child.tag), element)
    
    def collect_footnotes_pass(self):
        footnotes = []
        for elem in self.text:
            if isinstance(elem, Footnote):
                footnotes.append(elem)

        # Change footnotes come at the end of the text in numerals.
        if hasattr(self, "changeFootnote"):
            footnotes.append(self.changeFootnote)

        return footnotes

"""
Link

Text element to ber rendered as hyperlink.

Valid children: link, quote, footnote

Attributes:
 - to: link destination
 - link_text: text that will link to the destination
 - tail: ordered list of text elements that follow this link
 - element: XML element represented by this object
"""
class Link:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "link")
        self.element = element

        # well-formedness
        if is_empty(element.text):
            throw_error("a link must have a text", element)
        if is_empty(element.get("to")):
            throw_error("a link needs a destination", element)
        ensure_inserted_not_present(element)

        # values
        self.to = element.get("to")
        self.link_text = element.text

        self.tail = []
        if not is_empty(element.tail):
            self.tail.append(element.tail)
        
        for child in element:
            match child.tag:
                case "link":
                    self.tail.append(Link(child))
                case "quote":
                    self.tail.append(Quote(child))
                case "footnote":
                    self.tail.append(Footnote(child))
                case _:
                    throw_error("invalid link child <{}>".format(child.tag), element)


"""
Quote

Text element to quote a text segement.

Valid children: link, quote, footnote

Attributes:
 - quote: the text to be surrounded in quotes
 - tail: ordered list of text elements that follow this link
 - element: XML element represented by this object
"""
class Quote:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "quote")
        self.element = element

        # well-formedness
        if is_empty(element.text):
            throw_error("a quote must have a text", element)
        ensure_inserted_not_present(element)

        # values
        self.quote = element.text

        self.tail = []
        if not is_empty(element.tail):
            self.tail.append(element.tail)
        
        for child in element:
            match child.tag:
                case "link":
                    self.tail.append(Link(child))
                case "quote":
                    self.tail.append(Quote(child))
                case "footnote":
                    self.tail.append(Footnote(child))
                case _:
                    throw_error("invalid link child <{}>".format(child.tag), element)
                    

"""
Footnote

Text element to render a footnote at a particular text location.

Valid children: link, quote, footnote

Attributes:
 - text: the footnote text
 - number: the number for the footnote mark
 - tail: ordered list of text elements that follow this link
 - element: XML element represented by this object
"""
class Footnote:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "footnote")
        self.element = element

        # well-formedness
        if is_empty(element.text):
            throw_error("a footnote must have a text", element)
        ensure_inserted_not_present(element)

        # values
        self.text = element.text
        self.number = 0

        self.tail = []
        if not is_empty(element.tail):
            self.tail.append(element.tail)
        
        for child in element:
            match child.tag:
                case "link":
                    self.tail.append(Link(child))
                case "quote":
                    self.tail.append(Quote(child))
                case "footnote":
                    self.tail.append(Footnote(child))
                case _:
                    throw_error("invalid footnote child <{}>".format(child.tag), element)


"""
ChangeFootnote

Footnote to note how articles, etc. have changed over time. The tags "inserted", "changed", "deleted" are both
represented by this object. A element may have at most one change footnote. If the action is "deleted", the
element may not contain any other content.
The footnote mark of this footnote is rendered at a specific place, different for
each element (e.g. articles get their change footnote on the article number).

A change footnote will be rendered as text in the following way:
f"{actions_str} Beschluss in Tratankdum {agenda_item} der Sitzung {gremium_str} vom {meeting_date}
  ({motion_link}, {minutes_link}), {effect_str} seit {implementation_date}."

Valid children
 - number: number for the footnote mark (set by number_footnotes_pass()) 
 - action: one of the keys from the ACTIONS dict
 - action_str: appropriate text for change action (from ACTIONS dict)
 - gremium: abbreviation for a body changing the element (one of the keys from GREMIEN dict)
 - gremium_str: long name with appropriate article for Genitiv (from GREMIEN dict)
 - agenda_item: number (preferred) or name of the agenda item that changes the element
 - meeting_date: date of the meeting in YYYY-mm-dd format
 - implementation_date: date where the change takes effect in YYYY-mm-dd format
 - motion_link: link to the motion document outlining the change (only defined if present)
 - minutes_link: link to the minnutes of the meeting that decided this change (only defined if present)
 - tail: ordered list of text elements that follow this link
 - element: XML element represented by this object
"""
class ChangeFootnote:
    ACTIONS = {"changed": "Fassung gemäss dem",
               "deleted": "Aufgehoben durch den",
               "inserted": "Eingefügt durch den"}
    GREMIEN = {"MR": "des Mitgliederrats",
                   "FR": "des Fachvereinsrats",
                   "VS": "des VSETH-Vorstands",
                   "FinA": "des Finanzausschusses",
                   "ITA": "des IT-Ausschusses",
                   "SpEA": "des Spesen- und Entschädigungsausschusses",
                   "VEA": "des VSS-Evaluationsausschusses",
                   "GPK": "der Geschäftsprüfungskommission",
                   "Challenge": "der Kommission Challenge",
                   "Debattierclub": "der Kommission Debattierclub",
                   "MUN": "der Kommission ETH Model United Nations",
                   "ExBeKo": "der ExBeerience-Kommission",
                   "Filmstelle": "der Kommission Flimstelle",
                   "FLiK": "der Freiluftlichtbildschau-Kommission",
                   "F&C": "der Forum & Contact Kommission",
                   "FK": "der Fotokommission",
                   "GECo": "der Kommission Gaming and Entertainment Committee",
                   "KI": "der Kommission für Immobilien",
                   "Kulturstelle": "der Kommission Kulturstelle",
                   "Nightline": "der Kommission Nightline",
                   "Pub": "der Kommission PapperlaPub",
                   "Polykum": "der Kommission Polykum",
                   "SSC": "der Kommission Student Sustainability Commission",
                   "TheAlt": "der Kommission TheAlternative",
                   "TQ": "der Kommission Tankzquotient",
                   "SEK": "der Softwareentwicklungskommission"
                   }

    def __init__(self, element: etree.ElementBase):
        # Sanity
        assert(element.tag in self.ACTIONS.keys())
        self.element = element

        # well-formedness
        if is_empty(element.get("gremium")):
            throw_error("a change footnote must contain a gremium attribute", element)
        if element.get("gremium") not in self.GREMIEN.keys():
            throw_error(f"the gremium attribute \"{element.get('gremium')}\" of the change footnote is not one of the known gremien ({self.GREMIEN.keys()})", element)
        if is_empty(element.get("agenda_item")):
            throw_error("a change footnote must contain an agenda_item attribute", element)
        if is_empty(element.get("meeting_date")):
            throw_error("a change footnote must contain a meeting_date attribute", element)
        if is_empty(element.get("implementation_date")):
            throw_error("a change footnote must contain an implementation_date attribute", element)
        if not is_empty(element.text):
            throw_error("a change footnote must not contain text", element)
        ensure_inserted_not_present(element)
        if element.tag == "deleted" and not is_empty(element.tail):
            throw_error("a deleted element may not have any content", element)

        # values
        self.number = 0
        self.action = element.tag
        self.gremium = element.get("gremium")
        self.agenda_item = element.get("agenda_item")
        try:
            self.meeting_date = date.fromisoformat(element.get("meeting_date"))
        except Exception as e:
            throw_error(f"the meeting_date attribute \"{element.get('meeting_date')}\" is not a valid ISO 8601 date string: {e}", element)

        try:
            self.implementation_date = date.fromisoformat(element.get("implementation_date"))
        except Exception as e:
            throw_error(f"the implementation_date attribute \"{element.get('implementation_date')}\" is not a valid ISO 8601 date string: {e}", element)

        if not is_empty(element.get("motion_link")):
            self.motion_link = element.get("motion_link")
        if not is_empty(element.get("minutes_link")):
            self.minutes_link = element.get("minutes_link")

        try:
            self.action_str = self.ACTIONS[self.action]
        except Exception:
            throw_error("unreachable: actions should be checked", element)

        match self.action:
            case "changed" | "inserted":
                self.effect_str = "in Kraft"
            case "deleted":
                self.effect_str = "mit Wirkung"

        try:
            self.gremium_str = self.GREMIEN[self.gremium]
        except Exception:
            throw_error("unreachable: gremien should be checked", element)

        self.tail = []
        if not is_empty(element.tail):
            self.tail.append(element.tail)

        for child in element:
            match child:
                case _:
                    throw_error("a change footnote must not have children", element)
                    

# Functions to flatten container tags (articles, paragraphs, letters, numerals)
def process_articles(element: etree.ElementBase) -> list[Article]:
    # Sanity
    assert(element.tag == "articles")

    # Well-formedness
    if not is_empty(element.text):
        throw_error("articles may not contain text", element)
    if not is_empty(element.tail):
        throw_error("articles may not contain a tail (tail: {})".format(element.tail), element)
    ensure_inserted_not_present(element)

    articles = []
    for child in element:
        match child.tag:
            case "article":
                articles.append(Article(child))
            case _:
                throw_error("articles may only contain articles (duh)", child)

    return articles


def process_paragraphs(element: etree.ElementBase) -> list[Paragraph]:
    # Sanity
    assert(element.tag == "paragraphs")

    # Well-formedness
    if not is_empty(element.text):
        throw_error("paragraphs may not contain text", element)
    if not is_empty(element.tail):
        throw_error("paragraphs may not contain a tail (tail: {})".format(element.tail), element)
    ensure_inserted_not_present(element)

    paragraphs = []
    for child in element:
        match child.tag:
            case "paragraph":
                paragraphs.append(Paragraph(child))
            case _:
                throw_error("paragraphs may only contain paragraphs (duh)", child)

    return paragraphs


def process_letters(element: etree.ElementBase) -> tuple[list[Letter], str|None]:
    # Sanity
    assert(element.tag == "letters")

    # Well-formedness
    if not is_empty(element.text):
        throw_error("letters may not contain text", element)
    ensure_inserted_not_present(element)
    if not is_empty(element.tail):
        tail = element.tail
    else:
        tail = None

    letters = []
    for child in element:
        match child.tag:
            case "letter":
                letters.append(Letter(child))
            case _:
                throw_error("letters may only contain letters (duh)", child)

    return letters, tail


def process_numerals(element: etree.ElementBase) -> list[Numeral]:
    # Sanity
    assert(element.tag == "numerals")

    # Well-formedness
    if not is_empty(element.text):
        throw_error("numerals may not contain text", element)
    if not is_empty(element.tail):
        throw_error("numerals may not contain a tail (tail: {})".format(element.tail), element)
    ensure_inserted_not_present(element)

    numerals = []
    for child in element:
        match child.tag:
            case "numeral":
                numerals.append(Numeral(child))
            case _:
                throw_error("numerals may only contain numerals (duh)", child)

    return numerals

# Helper functions
def ensure_inserted_is_empty(element):
    if element.get("inserted") is not None and element.get("inserted") != "":
        throw_error("the attribute inserted must either be an empty string or not present", element)

def ensure_inserted_not_present(element):
    if element.get("inserted") is not None:
        throw_error("the attribute \"inserted\" must not be present in a {}".format(element.tag), element)

def is_empty(s):
    return s is None or s.strip() == ''

