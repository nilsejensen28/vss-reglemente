import pandas as pd
import numpy as np
import logging
import json

INPUT_DIR = "/home/nils/Dropbox/Documents/VSETH/Code/reglemente/input/"
OUTPUT_DIR = "/home/nils/Dropbox/Documents/VSETH/Code/reglemente/"
ADD_COMMENTS = True
LOGGING_LEVEL = logging.INFO
LANGUAGES = ["de", "fr"]


def main():
    logging.basicConfig()
    logging.getLogger().setLevel(LOGGING_LEVEL)
    FILES = INPUT_DIR + "files_test.json"
    files = json.load(open(FILES))
    for file in files["reglemente"]:
        name_short_de = file["name_short_de"]
        name_long_de = file["name_long_de"]
        name_short_fr = file["name_short_fr"]
        name_long_fr = file["name_long_fr"]
        names = {
            "de": (name_short_de, name_long_de),
            "fr": (name_short_fr, name_long_fr)
        }
        # Sanity check: Check that there is a name for every language
        for lang in LANGUAGES:
            if lang not in names:
                logging.log(
                    logging.WARNING, f"No name for language {lang} in {file['number']}")
                return

        number = file["number"]
        input_file = INPUT_DIR + number + ".xlsx"
        output_file = OUTPUT_DIR + number + ".xml"
        parse_file(input_file, output_file, number, names)
        logging.log(
            logging.INFO, f"Finished parsing {number}")


def parse_file(xlsx_input, xml_output, number, names):
    df_bylaws = pd.read_excel(xlsx_input, dtype=str)
    xml_file = xml_output
    reset_file(xml_file)
    parse_df(df_bylaws, xml_file, names, number)


def parse_df(df_bylaws: pd.DataFrame, xml_file: str, names, number):
    in_section = False
    in_subsection = False
    in_subsubsection = False
    in_articles = False
    with open(xml_file, "a") as f:
        f.write(
            f'<regulation id="{number}" title_de="{names["de"][1]}" short_de="{names["de"][0]}" title_fr="{names["fr"][1]}" short_fr="{names["fr"][0]}" original_implementation_date="2025-01-01">\n')
    for index, row in df_bylaws.iterrows():
        art_name = dict()
        art_text = dict()
        type_of_block = dict()
        for language in LANGUAGES:
            name = row["art_name_"+language]
            text = row["art_text_"+language]
            art_name[language] = name
            art_text[language] = text

            if text is np.NaN:
                if name is np.NaN:
                    # Empty line
                    type_of_block[language] = "EMPTY_LINE"
                else:
                    # We have a section
                    type_of_block[language] = "SECTION_HEADER"
            else:
                # We have an article
                type_of_block[language] = "ARTICLE"
        # Check if all languages have the same type of block
        if len(set(type_of_block.values())) != 1:
            logging.log(
                logging.WARNING, f"Line {index} has different types of blocks in different languages")
            return

        if type_of_block[LANGUAGES[0]] == "EMPTY_LINE":
            continue
        if type_of_block[LANGUAGES[0]] == "SECTION_HEADER":
            # Find out how deep we are
            number_of_dots = dict()
            for language in LANGUAGES:
                number_of_dots[language] = art_name[language].count(".")
            # Check if all languages have the same number of dots
            if len(set(number_of_dots.values())) != 1:
                logging.log(
                    logging.WARNING, f"Line {index} has different number of dots in different languages some headers are poorly formatted: {art_name}")
                return
            match number_of_dots[LANGUAGES[0]]:
                case 0:
                    logging.log(
                        logging.WARNING, f"{art_name[LANGUAGES[0]]} should be a header but doesn't seem to be")
                case 1:
                    parse_section(art_name, xml_file, in_section,
                                  in_subsection, in_subsubsection, in_articles)
                    in_section = True
                    in_subsection = False
                    in_subsubsection = False
                    in_articles = False
                case 2:
                    if in_section == False:
                        logging.log(
                            logging.WARNING, f"{art_name[LANGUAGES[0]]} should be a subsection but seems to be in no section")
                    parse_subsection(
                        art_name, xml_file, in_subsection, in_subsubsection, in_articles)
                    in_subsection = True
                    in_subsubsection = False
                    in_articles = False
                case 3:
                    if in_section == False or in_subsection == False:
                        logging.log(
                            logging.WARNING, f"{art_name[LANGUAGES[0]]} should be a subsection but seems to be in no section")
                    parse_subsubsection(
                        art_name, xml_file, in_subsubsection, in_articles)
                    in_subsubsection = True
                    in_articles = False
                case default:
                    logging.log(
                        logging.WARNING, f"{art_name[LANGUAGES[0]]} should be a header but doesn't seem to be")
            continue
        if type_of_block[LANGUAGES[0]] == "ARTICLE":
            if not in_articles:
                parse_articles(art_name, xml_file)
                in_articles = True
            parse_article(art_name, art_text, xml_file)
        else:
            logging.log(logging.WARNING,
                        f"Line {index} has an unknown type of block")
            return
    # Close everything at the end
    if in_articles:
        close_tag("articles", xml_file)
    if in_subsubsection:
        close_tag("subsubsection", xml_file)
    if in_subsection:
        close_tag("subsection", xml_file)
    if in_section:
        close_tag("section", xml_file)
    close_tag("regulation", xml_file)


def parse_section(names: str, xml_file: str, in_section: bool, in_subsection: bool, in_subsubsection: bool, in_articles: bool):
    if in_articles:
        close_tag("articles", xml_file)
    if in_subsubsection:
        close_tag("subsubsection", xml_file)
    if in_subsection:
        close_tag("subsection", xml_file)
    if in_section:
        close_tag("section", xml_file)
    attributes = {}
    for language in LANGUAGES:
        names[language] = names[language].split(".")[-1].lstrip().rstrip()
        attributes[f"title_{language}"] = names[language]
    open_tag("section", xml_file, attributes=attributes)


def parse_subsection(names: dict, xml_file: str, in_subsection: bool, in_subsubsection: bool, in_articles: bool):
    if in_articles:
        close_tag("articles", xml_file)
    if in_subsubsection:
        close_tag("subsubsection", xml_file)
    if in_subsection:
        close_tag("subsection", xml_file)
    attributes = {}
    for language in LANGUAGES:
        names[language] = names[language].split(".")[-1].lstrip().rstrip()
        attributes[f"title_{language}"] = names[language]
    open_tag("subsection", xml_file, attributes=attributes)


def parse_subsubsection(names: dict, xml_file: str, in_subsubsection: bool, in_articles: bool):
    if in_articles:
        close_tag("articles", xml_file)
    if in_subsubsection:
        close_tag("subsubsection", xml_file)
    attributes = {}
    for language in LANGUAGES:
        names[language] = names[language].split(".")[-1].lstrip().rstrip()
        attributes[f"title_{language}"] = names[language]
    open_tag("subsubsection", xml_file, attributes=attributes)


def parse_articles(names: dict,  xml_file: str):
    for language in LANGUAGES:
        name = names[language]
        prefix = name.split(".")[0]
        if not prefix == "Art":
            logging.log(logging.WARNING,
                        f'{name} should be an article name but doesnt seem to be')
    open_tag("articles", xml_file)


def parse_article(name: str, text: str, xml_file: str):
    attributes = {}
    for language in LANGUAGES:
        try:
            title = name[language].split("\n")[1].lstrip().rstrip()
            attributes[f"title_{language}"] = title
        except Exception:
            logging.log(logging.WARNING, f"{name} is not a valid article name")
            return
    open_tag("article", xml_file, attributes=attributes)
    # Find out if we have a single or multiple paragraphs
    article_type = set()
    for language in LANGUAGES:
        if text[language] is np.NaN:
            article_type.add("EMPTY")
        if text[language][0:2] == "1 ":
            article_type.add("MULTIPLE_PARAGRAPHS")
        else:
            article_type.add("SINGLE_PARAGRAPH")
    if len(article_type) != 1:
        logging.log(
            logging.WARNING, f"Article {name} has different types of articles in different languages")
        return
    if "EMPTY" in article_type:
        return
    if "MULTIPLE_PARAGRAPHS" in article_type:
        parse_paragraphs(text, xml_file)
    else:
        parse_paragraph(text=text, xml_file=xml_file)
    close_tag("article", xml_file)


def parse_paragraphs(text: dict, xml_file: str):
    open_tag("paragraphs", xml_file)
    logging.log(logging.DEBUG, f'Parsing paragraphs "{text}"')
    lines_temporary = {language: text[language].split(
        "\n") for language in LANGUAGES}
    # Remove empty lines from back
    for language in LANGUAGES:
        # Remove all empty strings at the end
        while lines_temporary[language][-1] == "":
            lines_temporary[language] = lines_temporary[language][:-1]
            logging.debug(
                f"Removed empty line from {lines_temporary[language]}")

    # Check if the number of lines is the same for all languages
    if len(set([len(lines) for lines in lines_temporary.values()])) != 1:
        logging.log(
            logging.WARNING, f"Paragraphs {text} have different number of lines in different languages")
        return
    lines = []
    for index in range(len(lines_temporary[LANGUAGES[0]])):
        lines.append(
            {language: lines_temporary[language][index] for language in LANGUAGES})
    current_paragraph = {language: "" for language in LANGUAGES}
    # Set of all possible numeric starts
    numeric_start = {f"{i} " for i in range(1, 10)}
    for line in lines:
        # Check if the line starts with a number followed by a space
        type_of_line = set()
        for language in LANGUAGES:
            if line[language] is np.NaN:
                type_of_line.add("EMPTY")
            elif line[language][0:2] in numeric_start:
                type_of_line.add("NEW_PARAGRAPH")
            else:
                type_of_line.add("CONTINUATION")
        if len(type_of_line) != 1:
            logging.log(
                logging.WARNING, f"Line {line} has different types of lines in different languages")
            return
        if "NEW_PARAGRAPH" in type_of_line:
            if current_paragraph[LANGUAGES[0]] != "":
                open_tag("paragraph", xml_file)
                parse_paragraph(current_paragraph, xml_file)
                close_tag("paragraph", xml_file)
            current_paragraph = line
            # Remove the number and the space
            for language in LANGUAGES:
                if current_paragraph[language][0:2] in numeric_start:
                    # Remove the number and the space
                    current_paragraph[language] = current_paragraph[language][2:]
        else:
            for language in LANGUAGES:
                current_paragraph[language] += line[language]
    # Parse the last paragraph
    if current_paragraph[LANGUAGES[0]] != "":
        open_tag("paragraph", xml_file)
        parse_paragraph(current_paragraph, xml_file)
        close_tag("paragraph", xml_file)
    close_tag("paragraphs", xml_file)


def parse_paragraph(text: dict, xml_file: str):
    logging.log(logging.DEBUG, f'Parsing paragraph "{text}"')
    # Construct a list of dicts with the text and the language
    lines_temporary = {language: text[language].split(
        "\n") for language in LANGUAGES}
    # Remove empty lines from back
    for language in LANGUAGES:
        # Remove all empty strings at the end
        while lines_temporary[language][-1] == "":
            lines_temporary[language] = lines_temporary[language][:-1]
            logging.debug(
                f"Removed empty line from {lines_temporary[language]}")
    # Check if the number of lines is the same for all languages
    if len(set([len(lines) for lines in lines_temporary.values()])) != 1:
        logging.log(
            logging.WARNING, f"Paragraph {text} has different number of lines in different languages")
        return
    lines = []
    for index in range(len(lines_temporary[LANGUAGES[0]])):
        lines.append(
            {language: lines_temporary[language][index] for language in LANGUAGES})
    first_line = lines[0]
    for language in LANGUAGES:
        parse_text(first_line[language], xml_file, language)
    if len(lines) > 1:
        parse_letters(lines[1:], xml_file)
    pass


def parse_letters(lines: list, xml_file: str):
    open_tag("letters", xml_file)
    for line in lines:
        if line[LANGUAGES[0]] != "":
            parse_letter(line, xml_file)
    close_tag("letters", xml_file)


def parse_letter(text: dict, xml_file: str):
    open_tag("letter", xml_file)
    for language in LANGUAGES:
        parse_text(text[language], xml_file, language)
    close_tag("letter", xml_file)


def parse_text(text: str, xml_file: str, language):
    logging.log(logging.DEBUG, f'Parsing text "{text}"')
    open_tag("text", xml_file, attributes={"language": language})
    # Check that there are no double spaces
    text = text.replace("  ", " ")
    parts = text.split('"')
    if len(parts) % 2 != 1:
        logging.log(logging.WARNING,
                    "The number of quotes in {text} is not even")
        write_text(text, xml_file)
        return
    for index, part in enumerate(parts):
        if index % 2 == 1:
            open_tag("quote", xml_file, new_line=False)
            write_text(part, xml_file)
            close_tag("quote", xml_file, new_line=False)
        else:
            write_text(part, xml_file)
    write_text("\n", xml_file)
    close_tag("text", xml_file)


def close_tag(tag: str, xml_file: str, new_line=True):
    with open(xml_file, "a") as f:
        f.write(f'</{tag}>')
        if new_line:
            f.write("\n")


def open_tag(tag: str, xml_file: str, title="", new_line=True, attributes=None):
    if attributes is None:
        attributes = {}
    if title != "":
        attributes["title"] = title
    tags = ""
    for attribute, value in attributes.items():
        tags += f' {attribute}="{value}"'
    with open(xml_file, "a") as f:
        if new_line:
            f.write(f'<{tag}{tags}>\n')
        else:
            f.write(f'<{tag}{tags}>')


def write_text(text: str, xml_file: str):
    text = text.replace("⅔", "Zweidrittel")
    text = text.replace("¾", "Dreiviertel")
    with open(xml_file, "a") as f:
        f.write(text)


def remove_last_line(xml_file):
    lines = None
    with open(xml_file, "r") as f:
        lines = f.readlines()
    last_line = lines[-1]
    lines = lines[:-1]
    with open(xml_file, "w") as f:
        f.write("".join(lines))


def reset_file(xml_file):
    # Create a new empty file
    with open(xml_file, "w") as f:
        f.write("")


if __name__ == "__main__":
    main()
