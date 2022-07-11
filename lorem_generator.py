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


__all__ = [
    "lorem_generator",
]


class LoremGenerator:
    default_chars_len = 2
    default_word_count = 48

    def __init__(self):
        self.input_text = self.read_text()

    @staticmethod
    def read_text() -> str:
        data_directory = "./russian_text_data"
        path = Path(data_directory).absolute()
        if not path.is_dir():
            msg = "The directory `russian_text_data` should be in the root of the project"
            raise ValueError(msg)
        files = (
            file
            for file in path.iterdir()
            if str(file).endswith('.txt')
        )

        text = '\n'.join(open(file, encoding="utf8").read() for file in files)
        text = text.lower()
        text = re.sub(r'[^а-яё\s.!?,]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def generate_raw_lorem(self, words: int, chars_len: int) -> str:
        input_text = self.input_text + self.input_text[:chars_len]
        max_index = len(self.input_text) - chars_len

        resulting_text = " "
        current_chars = ""

        while resulting_text.count(" ") < words + 1:
            # get chars
            start = randint(0, max_index)
            first_index = input_text.find(current_chars, start, max_index)
            if first_index == -1:
                first_index = input_text.find(current_chars)
            first_index += chars_len
            current_chars = input_text[first_index : first_index + chars_len]

            # add chars
            chars_to_set = current_chars

            if resulting_text[-1] == " " and chars_to_set[0] == " ":
                # this should not happen, since there are no two spaces
                # in a row, but still
                chars_to_set = chars_to_set[1:]

            # no repetitive punctuation characters
            if (resulting_text[-1] in ".!?,") and (chars_to_set[0] in ".!?,"):
                chars_to_set = chars_to_set[1:]

            resulting_text += chars_to_set

        return resulting_text

    @staticmethod
    def postprocess_lorem(text: str) -> str:
        """
        Processing raw text into humanoid text.
        """

        if text[0] == '.':
            text = text[1:]
        text = text.lstrip().rstrip()

        # only one punctuation mark consecutive
        dot_dot_pattern = re.compile(r'([.!?,])+')
        text = dot_dot_pattern.sub(r'\1', text)

        # spaces after punctuation marks
        dot_word_pattern = re.compile(r'([.!?,])([а-яё])')
        text = dot_word_pattern.sub(r'\1 \2', text)

        # no spaces before punctuation marks
        space_dot_pattern = re.compile(r'(\s)+([.!?,])')
        text = space_dot_pattern.sub(r'\2', text)

        # the first letter in the sentence should be capitalized
        sentences_pattern = re.compile(r'([.!?]\s)')
        text = ''.join(
            sentence.capitalize()
            for sentence in sentences_pattern.split(text)
        )

        if text[-1] not in ".!?":
            if text[-1] == ",":
                text = text[:-1]
            text += '.'

        return text

    def generate_lorem(self, words=default_word_count, chars_len=default_chars_len) -> str:
        resulting_text = self.generate_raw_lorem(words, chars_len)
        resulting_text = self.postprocess_lorem(resulting_text)
        return resulting_text


lorem_generator = LoremGenerator()


if __name__ == '__main__':
    print(lorem_generator.generate_lorem())
