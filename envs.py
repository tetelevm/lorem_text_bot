from ast import literal_eval
from pathlib import Path


__all__ = [
    "envs",
]


def parse_envs() -> dict:
    """
    Parses the secret variables specified in the gitigrored `.envs` file.
    Variables must be specified on separate in the format `"name": value`,
    the value must be a plain python type. The comment after the hashtag
    character can also be after the value.
    An example is in the `.envs_example` file.
    """

    current_path = Path().absolute()
    envs_file = current_path / ".envs"
    try:
        with open(envs_file, "r") as file:
            text = file.readlines()
    except FileNotFoundError:
        raise ValueError("Requires the settings file `.envs` in the root of the project")

    # breaks if hashtag somewhere in the string value
    clean_text = [line[:line.find("#")] for line in text]
    envs_dict = "{" + ",".join(filter(bool, clean_text)) + "}"
    return literal_eval(envs_dict)


envs = parse_envs()
