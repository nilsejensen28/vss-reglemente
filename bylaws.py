#!/usr/bin/env python
from lxml import etree, ElementInclude


# https://stackoverflow.com/a/69618810/6337138
def XinlcudeLoader(href, parse, encoding=None, parser=etree.XMLParser(remove_comments=True)):
    ret = ElementInclude._lxml_default_loader(href, parse, encoding, parser)
    ret.attrib["{http://www.w3.org/XML/1998/namespace}base"] = href
    ret.attrib["filename"] = href
    return ret


art_counter = 0
abs_counter = 0
lit_counter = 0
num_counter = 0
sec_counter = 0
subsec_counter = 0
subsubsec_counter = 0
filename = None


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


class Bylaws:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "bylaws")

        # Well-formedness
        if not is_empty(element.text):
            throw_error("Bylaws may not contain text", element)
        if not is_empty(element.tail):
            throw_error("Bylaws may not have a tail (tail: {})".format(element.tail), element)
        if is_empty(element.get("title")):
            throw_error("Bylaws must contain a title", element)

        # Values
        self.title = element.get("title")

        self.regulations = []
        for child in element:
            match child.tag:
                case "regulation":
                    self.regulations.append(Regulation(child))
                case _:
                    throw_error("Bylaws only contain regulations", element)


class Regulation:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter, filename
        # Sanity
        assert(element.tag == "regulation")

        # Well-formedness
        if not is_empty(element.text):
            throw_error("a regulation may not contain text", element)
        if not is_empty(element.tail):
            throw_error("a regulation may not have a tail (tail: {})".format(element.tail), element)
        if is_empty(element.get("title")):
            throw_error("a regulation must have a title", element)
        if is_empty(element.get("id")):
            throw_error("a regulation must contain an id", element)

        # reset counters
        art_counter, sec_counter = 0, 0

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
                    if is_empty(self.sections):
                        self.articles = process_articles(child)
                    else:
                        throw_error("a regulation may only contain articles before any sections", element)
                case _:
                    throw_error("a regulation only contain articles, a preamble and sections", element)


class Preamble:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "preamble")

        # Well-formedness
        if not is_empty(element.tail):
            throw_error("a preamble may not have a tail", element)

        # Values
        self.text = []
        if not is_empty(element.text):
            self.text.append(element.text)

        for child in element:
            match child:
                case "link":
                    self.text.append(Link(child))
                case "quote":
                    self.text.append(Quote(child))
                case _:
                    throw_error("invalid preamble child <{}>".format(child.tag), element)



class Section:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "section")

        # Well-formedness
        if not is_empty(element.text):
            throw_error("a section my not contain text on its own", element)
        if not is_empty(element.tail):
            throw_error("a section my not have a tail (tail: {})".format(element.tail), element)
        if is_empty(element.get("title")):
            throw_error("a section must have a title", element)

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


class Subsection:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "subsection")

        # Well-formedness
        if not is_empty(element.text):
            throw_error("a subsection my not contain text on its own", element)
        if not is_empty(element.tail):
            throw_error("a subsection my not have a tail (tail: {})".format(element.tail), element)
        if is_empty(element.get("title")):
            throw_error("a subsection must have a title", element)

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


class Subsubsection:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "subsubsection")

        # Well-formedness
        if not is_empty(element.text):
            throw_error("a subsubsection my not contain text on its own", element)
        if not is_empty(element.tail):
            throw_error("a subsubsection my not have a tail (tail: {})".format(element.tail), element)
        if is_empty(element.get("title")):
            throw_error("a subsubsection must have a title", element)

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


class Article:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "article")

        # well-formedness
        if not is_empty(element.tail):
            throw_error("an article may not have a tail (tail: {})".format(element.tail), element)
        if is_empty(element.get("title")):
            throw_error("an article needs a title", element)

        # reset counters
        abs_counter, lit_counter = 0, 0

        # increment article counter
        art_counter += 1

        # values
        self.title = element.get("title")
        self.number = art_counter

        self.text = []
        self.paragraphs = []
        self.letters = []
        self.letters_tail = None

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
                case _:
                    throw_error("invalid article child {}".format(child.tag), element)



class Paragraph:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "paragraph")

        # well-formedness
        if not is_empty(element.tail):
            throw_error("a paragraph may not have a tail (tail: {})".format(element.tail), element)

        # reset counters
        lit_counter = 0

        # increment paragraph number
        abs_counter += 1

        # values
        self.number = abs_counter

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
                case _:
                    throw_error("invalid paragraph child <{}>".format(child.tag), element)



class Letter:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "letter")

        # well-formedness
        if not is_empty(element.tail):
            throw_error("a letter may not have a tail (tail: {})".format(element.tail), element)
        
        # reset counter
        num_counter = 0

        # increment letter counter
        lit_counter += 1

        # values
        self.number = lit_counter
        
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
                case _:
                    throw_error("invalid letter child {}".format(child.tag), element)


class Numeral:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "numeral")

        # well-formedness
        if not is_empty(element.tail):
            throw_error("a numeral may not have a tail (tail: {})".format(element.tail), element)

        # increment numeral counter
        num_counter += 1

        # values
        self.number = num_counter

        self.text = []

        if not is_empty(element.text):
            self.text.append(element.text)

        for child in element:
            match child.tag:
                case "link":
                    self.text.append(Link(child))
                case "quote":
                    self.text.append(Quote(child))
                case _:
                    throw_error("invalid numeral child {}".format(child.tag), element)


class Link:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "link")

        # well-formedness
        if is_empty(element.text):
            throw_error("a link must have a text", element)
        if is_empty(element.get("to")):
            throw_error("a link needs a destination", element)

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
                case _:
                    throw_error("invalid link child <{}>".format(child.tag), element)


class Quote:
    def __init__(self, element: etree.ElementBase) -> None:
        global sec_counter, subsec_counter, subsubsec_counter, art_counter, abs_counter, lit_counter, num_counter
        # Sanity
        assert(element.tag == "quote")

        # well-formedness
        if is_empty(element.text):
            throw_error("a quote must have a text", element)

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
                case _:
                    throw_error("invalid link child <{}>".format(child.tag), element)
                    

def process_articles(element: etree.ElementBase) -> list[Article]:
    # Sanity
    assert(element.tag == "articles")

    # Well-formedness
    if not is_empty(element.text):
        throw_error("articles may not contain text", element)
    if not is_empty(element.tail):
        throw_error("articles may not contain a tail (tail: {})".format(element.tail), element)

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

    numerals = []
    for child in element:
        match child.tag:
            case "numeral":
                numerals.append(Numeral(child))
            case _:
                throw_error("numerals may only contain numerals (duh)", child)

    return numerals


def is_empty(s):
    return s is None or s.strip() == ''

