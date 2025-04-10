import csv
import importlib.resources


def load_table():
    with importlib.resources.open_text(
        "SanskritTransliteration",
        "transliteration_table.csv",
        encoding="utf-8",
    ) as f:
    # with open("transliteration_table.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        return list(reader)


def transliterate(
    text: str,
    input_method: str,
    output_method: str,
)-> str:
    """
    Transliterate text from one method to another.
    :param text: The text to transliterate.
    :param input_method: The input method to transliterate from.
    :param output_method: The output method to transliterate to.
    :return: The transliterated text.
    """

    # load table
    table = load_table()
    
    # get header
    table_iter = iter(table)
    header = next(table_iter)

    # transliterate
    for row in table:
        text = text.replace(
            row[header.index(input_method)],
            row[header.index(output_method)],
        )

    return text


if __name__ == "__main__":
    s = transliterate(
        "agn;im ii;le pur;ohitam",
        "tf",
        "iso",
    )
    print(s)
