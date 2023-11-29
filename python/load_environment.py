"""
load_environment.py

Moves the settings from the plugin's data.json file into a .env file and loads them into
the environment.
"""

import json
import os

from dotenv import load_dotenv


def load_environment() -> None:
    """Loads the plugin's settings into the environment."""

    current_dir = os.getcwd()

    # need to go up one directory to get to the plugin's root directory
    data_file_path = os.path.join(current_dir, "..", "data.json")
    env_file_path = os.path.join(current_dir, ".env")

    with open(data_file_path, "r", encoding="utf-8") as data_file:
        data = json.load(data_file)

    with open(env_file_path, "w", encoding="utf-8") as env_file:
        env_file.write(f"""OPENAI_API_KEY=\"{data['openaiApiKey']}\"""")

    load_dotenv()


if __name__ == "__main__":
    load_environment()
