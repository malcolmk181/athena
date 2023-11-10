"""
file_handling.py

Contains functions for interacting with files from the Obsidian vault.
"""

import glob
import json
import os
import uuid


def collect_file_paths_from_vault() -> list[str]:
    """Returns the file paths of the markdown files in the vault directory."""

    return glob.glob("../../../../*.md")


def collect_file_names_from_vault() -> list[str]:
    """Returns the file names of the markdown files in the vault directory."""

    file_paths = glob.glob("../../../../*.md")
    file_names = [os.path.basename(path) for path in file_paths]

    return file_names


def create_new_note_store(overwrite_existing_store: bool = False) -> None:
    """Creates a new json file to store information about the notes. Does nothing if
    there is already an existing store and overwrite_existing_store is False.
    """

    if os.path.exists("file_store.json") and not overwrite_existing_store:
        print("File store already exists. Skipping file store creation.")
        return

    file_store = {}

    notes = collect_file_paths_from_vault()

    for note in notes:
        file_store[os.path.basename(note)] = {
            "last_modified": os.path.getmtime(note),
            "uuid": str(uuid.uuid4()),  # uuid object is not serializable
            "chunks": [],
        }

    with open("file_store.json", "w", encoding="utf-8") as json_file:
        json.dump(file_store, json_file)


def file_store_exists() -> bool:
    """Checks the existence of the file store."""

    return os.path.exists("file_store.json")


def load_file_store() -> dict | None:
    """Returns a loaded dictionary of the file store. If the file store does not exist,
    then returns None.
    """

    if not file_store_exists():
        return None

    with open("file_store.json", "r", encoding="utf-8") as json_file:
        loaded = json.load(json_file)

    return loaded


def update_file_store(file_store: dict) -> None:
    """Overwrite the file store with a dictionary."""

    with open("file_store.json", "w", encoding="utf-8") as json_file:
        json.dump(file_store, json_file)
