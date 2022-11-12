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
from typing import Dict, Union, List, Callable


__all__ = [
    "lorem_generator",
    "chinese_generator",
]


# === for preprocessing ===============================================
# Functions for text preprocessing, not used in the application

def get_all_chars(path):
    print(repr("".join(sorted(set(open(path).read())))))

def clear_text(path, to=None):
    import re
    with open(path, "r") as file:
        text = file.read()
    text = re.sub(r"[\s]+", " ", text)
    text = re.sub(r"(\s)+([.!?,])", r"\2", text)
    text = re.sub(r"([.!?,])+", r"\1", text)
    text = re.sub(r"([.!?,])([^\s])", r"\1 \2", text)
    text = re.sub(r"\s+", " ", text)
    to = to or path
    with open(to, "w") as file:
        file.write(text)

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
    default_word_count = 64
    default_chars_len = 2

    punctuation = r".!?,"
    end_sentence = punctuation.replace(",", "")
    lang_chars = {
        "ru": r"а-яё",
        "en": r"a-z",
        "el": r"α-ω",
        "tt": r"а-яёҗңүһәө",
        "nl": r"a-z",
        "hy": "ա-և",
        "cs": r"a-záãäåçèéëíóöøúüýčďěňřšťůžίό",
    }

    text_data: Dict[str, str]
    languages: List[str]

    def __init__(self):
        self.text_data = self.collect_data(self.data_directory)
        self.languages = list(self.text_data)
        self.patterns = {
            "multi_dot": re.compile(fr"([{self.punctuation}])+"),
            "multi_space": re.compile(r"\s+"),
            "dot_word": re.compile(fr"([{self.punctuation}])([^\s])"),
            "space_dot": re.compile(fr"(\s)+([{self.punctuation}])"),
            "end_sentences": re.compile(fr"([{self.end_sentence}]\s)"),
            "all_punctuation": re.compile(f"[{self.punctuation}]"),
        }

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

    def generate_raw_lorem(
            self,
            language: str,
            chars_len: int,
            is_need_to_stop_condition: Callable[[str], bool]
    ) -> str:
        """
        Generates Lorem.
        To do this, it selects several characters into the buffer, and
        then searches for them in the text (in a random place), replaces
        the buffer with the characters next to them, and repeats again.
        The resulting text is the join of all the buffers used.

        The last argument is the function that determines when the
        generation stops.
        """

        text = self.text_data[language]
        text_len = len(text)
        looped_text = text + text[:chars_len]

        resulting_text = ""
        buffer = ""
        while not is_need_to_stop_condition(resulting_text):
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

        # no spaces before punctuation marks
        text = self.patterns["space_dot"].sub(r"\2", text)

        # only one punctuation mark consecutive
        text = self.patterns["multi_dot"].sub(r"\1", text)

        # should no punctuation mark at the beginning of
        if text[0] in self.punctuation:
            text = text[1:]
        text = text.strip()

        # spaces after punctuation marks
        text = self.patterns["dot_word"].sub(r"\1 \2", text)

        # only one space is consecutive
        text = self.patterns["multi_space"].sub(" ", text)

        # the first letter in the sentence should be capitalized
        text = "".join(
            sentence.capitalize()
            for sentence in self.patterns["end_sentences"].split(text)
        )

        if text and text[-1] not in self.punctuation:
            if text[-1] == ",":
                text = text[:-1]
            text += "."

        return text

    def generate_lorem(
            self,
            language: str = default_language,
            words: int = default_word_count,
            chars_len: int = default_chars_len
    ) -> str:
        """
        The main method of the class, generates the Lorem and fixes it
        to the correct form.
        """

        if language not in self.languages:
            raise ValueError(f"Unknown language {language}")

        is_sufficient_text = lambda text: text.count(" ") >= words
        resulting_text = self.generate_raw_lorem(language, chars_len, is_sufficient_text)
        resulting_text = self.postprocess_lorem(resulting_text)
        return resulting_text

    def __call__(
            self,
            language: str = default_language,
            words: int = default_word_count,
            chars_len: int = default_chars_len
    ) -> str:
        return self.generate_lorem(language, words, chars_len)

    def generate_sentences(
            self,
            language: str = default_language,
            sentences_count: int = 1,
            chars_len: int = default_chars_len
    ) -> str:
        """
        Generates several Lorem sentences.
        """

        if language not in self.languages:
            raise ValueError(f"Unknown language {language}")

        # as `self._sentences_pattern`, but without a space at the end
        sentences_end_pat = re.compile(fr"([{self.end_sentence}])")

        def is_sufficient(text: str) -> bool:
            text = text.lstrip(self.end_sentence + " ")
            return len(sentences_end_pat.findall(text)) >= sentences_count

        resulting_text = self.generate_raw_lorem(language, chars_len, is_sufficient)
        resulting_text = resulting_text.lstrip(self.end_sentence + " ")
        split_text = sentences_end_pat.split(resulting_text)
        resulting_text = "".join(split_text[:sentences_count * 2])

        resulting_text = self.postprocess_lorem(resulting_text)
        return resulting_text

    def clear_text(self, text: str) -> str:
        """
        Clears the text of punctuation marks and converts it to lower
        case.
        """
        return self.patterns["all_punctuation"].sub("", text).lower()


class ChineseGenerator:
    """
    A class for a small task - storing text in Chinese and giving out a
    random number of characters from it.
    """

    chinese_path = "./text_data/chinese.txt"

    chinese: str
    len: int

    def __init__(self):
        with open(self.chinese_path, "r", encoding="utf8") as chinese_file:
            self.chinese = chinese_file.read()
        self.len = len(self.chinese)

    def get_chinese(self, count: int) -> str:
        """
        Returns several consecutive Chinese characters from a random
        place in the text.
        """

        if count > self.len:
            raise ValueError(f"Requires more text ({count}) than there is ({self.len})")

        cursor = randint(0, self.len)
        if cursor + count < self.len:
            return self.chinese[cursor:cursor+count]

        first_part = self.chinese[cursor:]
        second_part = self.chinese[:count - (self.len-cursor) + 1]
        return first_part + second_part


lorem_generator = LoremGenerator()
chinese_generator = ChineseGenerator()


if __name__ == "__main__":
    print(lorem_generator.generate_lorem())
    print()
    print(lorem_generator.generate_sentences(sentences_count=3))
    print()
    print(chinese_generator.get_chinese(48))
