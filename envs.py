from ast import literal_eval
from pathlib import Path


__all__ = [
    "envs",
]


def parse_envs() -> dict:
    """
    Parses the secret variables specified in the gitigrored `.envs` file.
    Variables must be specified on separate in the format `"name": value`,
    the value must be a plain python type.
    An example is in the `.envs_example` file.
    """

    current_path = Path().absolute()
    envs_file = current_path / ".envs"
    try:
        with open(envs_file, "r") as file:
            envs_str = [line.replace("\n", "") for line in file.readlines()]
    except FileNotFoundError:
        raise ValueError("Requires the settings file `.envs' in the root of the project")

    envs_dict = "{" + ",".join(filter(None, envs_str)) + "}"
    return literal_eval(envs_dict)


envs = parse_envs()
