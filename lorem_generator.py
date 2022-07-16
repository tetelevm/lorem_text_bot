"""
Pseudoword generator using books/text.
Requires prefetched data.

The algorithm is as follows:
  1) collect the entire text array
  2) move the cursor to a random place
  3) memorize the next two letters and write them into the resulting text
  4) move the cursor to a random place
  5) move the cursor forward to the first occurrence of these letters
     in the text
  6) if the resulting text is still insufficient, return to step 3)
"""

import re
from random import randint
from pathlib import Path
from typing import Dict, Union


__all__ = [
    "lorem_generator",
]


# === for preprocessing ===============================================
# Functions for text preprocessing, not used in the application

def reduce_lines(path, to=None):
    import re
    with open(path, "r") as file:
        text = file.read()
    text = re.sub(r"\s+", " ", text)
    result = ""
    while text:
        ind = text.find(" ", 70)
        if ind != -1:
            result += text[:ind] + "\n"
            text = text[ind + 1:]
        else:
            result += text + "\n"
            text = ""
    to = to or path
    with open(to, "w") as file:
        file.write(result)

# =====================================================================


class LoremGenerator:
    """
    A class that generates a lorem.
    """

    data_directory = "./text_data"

    default_language = "ru"
    default_word_count = 48
    default_chars_len = 2

    punctuation = r".!?,"
    lang_chars = {
        "ru": r"а-яё",
        "en": r"a-z",
        "el": r"α-ω",
    }

    text_data: Dict[str, str]

    def __init__(self):
        self.text_data = self.collect_data(self.data_directory)

        self._multi_dot_pat = re.compile(fr"([{self.punctuation}])+")
        self._dot_word_pat = re.compile(fr"([{self.punctuation}])([^\s])")
        self._space_dot_pat = re.compile(fr"(\s)+([{self.punctuation}])")
        punct_without_comma = self.punctuation.replace(",", "")
        self._sentences_pattern = re.compile(fr"([{punct_without_comma}]\s)")

    def collect_data(self, data_directory: str) -> Dict[str, str]:
        """
        Looks for subfolders of languages and reads all the text from
        them.
        """

        data_path = Path(data_directory).absolute()
        if not data_path.is_dir():
            msg = "The directory `text_data` should be in the root of the project"
            raise ValueError(msg)

        languages = [
            folder
            for folder in data_path.iterdir()
            if folder.is_dir()
        ]
        if not languages:
            raise ValueError("There are no language subfolders in the directory.")

        text_data = dict()
        for lang_dir in languages:
            text = self.read_language_data(lang_dir)
            if text is not None:
                text_data[lang_dir.name] = text

        return text_data

    def read_language_data(self, lang_dir: Path) -> Union[str, None]:
        """
        Reads all files in `.txt.` format from a subfolder, joins them
        into a single text and cleans the resulting text (removes line
        breaks and extra spaces, translates into lowercase, tries to
        remove extra characters).
        """
        files = [
            file
            for file in lang_dir.iterdir()
            if str(file).endswith(".txt")
        ]
        if not files:
            return None

        text = ""
        for file_path in files:
            with open(file_path, "r", encoding="utf8") as file:
                text += file.read() + "\n"

        text = text.lower()
        chars = self.lang_chars.get(lang_dir.name, None)
        if chars is not None:
            text = re.sub(fr"[^{chars}\s{self.punctuation}]", " ", text)
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        return text

    def generate_raw_lorem(self, language: str, words: int, chars_len: int) -> str:
        """
        Generates Lorem.
        To do this, it selects several characters into the buffer, and
        then searches for them in the text (in a random place), replaces
        the buffer with the characters next to them, and repeats again.
        The resulting text is the join of all the buffers used.
        """

        text = self.text_data[language]
        text_len = len(text)
        looped_text = text + text[:chars_len]

        resulting_text = ""
        buffer = ""
        while resulting_text.count(" ") < words:
            start_ind = randint(0, text_len)
            first_index = looped_text.find(buffer, start_ind, text_len)
            if first_index == -1:
                first_index = looped_text.find(buffer)
            next_symbols_ind = first_index + chars_len

            buffer = looped_text[next_symbols_ind: next_symbols_ind + chars_len]
            resulting_text += buffer

        return resulting_text

    def postprocess_lorem(self, text: str) -> str:
        """
        Processing raw lorem into correct humanoid text.
        """

        # only one punctuation mark consecutive
        text = self._multi_dot_pat.sub(r"\1", text)

        # should no punctuation mark at the beginning of
        if text[0] in self.punctuation:
            text = text[1:]
        text = text.strip()

        # spaces after punctuation marks
        text = self._dot_word_pat.sub(r"\1 \2", text)

        # no spaces before punctuation marks
        text = self._space_dot_pat.sub(r"\2", text)

        # the first letter in the sentence should be capitalized
        text = "".join(
            sentence.capitalize()
            for sentence in self._sentences_pattern.split(text)
        )

        if text[-1] not in self.punctuation:
            if text[-1] == ",":
                text = text[:-1]
            text += "."

        return text

    def generate_lorem(self, language=None, words=None, chars_len=None) -> str:
        """
        The main method of the class, generates the Lorem and fixes it
        to the correct form.
        """

        words = words or self.default_word_count
        chars_len = chars_len or self.default_chars_len
        language = language or self.default_language
        if language not in self.text_data:
            raise ValueError(f"Unknown language {language}")

        resulting_text = self.generate_raw_lorem(language, words, chars_len)
        resulting_text = self.postprocess_lorem(resulting_text)
        return resulting_text


lorem_generator = LoremGenerator()


if __name__ == "__main__":
    print(lorem_generator.generate_lorem())
