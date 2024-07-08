"""Module for parsing a mod page on Modrinth and extracting whether the mod is server side."""

import json
import pathlib
import re
from time import sleep

from labrinth import LabrinthAPI


def parse_markdown_links(folder_path: pathlib.Path, file_name: str) -> dict[str, str]:
    """Parse a markdown file and return a dictionary of links.

    Args:
        folder_path (pathlib.Path): The path to the folder containing the markdown file.
        file_name (str): The name of the markdown file.

    Returns:
        dict[str, str]: A dictionary of links where the key is the text and the value is the URL.
    """
    file_path = folder_path / file_name

    links_dict = {}
    link_pattern = re.compile(r"\[([^\]]+)\]\((http[s]?://[^\)]+)\)")

    with open(file_path, "r") as file:
        for line in file:
            # NOTE: this excludes mods that are not hosted on Modrinth
            matches = link_pattern.findall(line)
            for text, url in matches:
                mod_id = re.split(r"(resourcepack|mod|shader)/", url)[-1]
                if not mod_id:
                    print(f"{text} failed to be parsed.")
                    continue
                links_dict[mod_id] = {"name": text, "url": url}

    return links_dict


def is_server_side_mod(project: dict) -> bool:
    """Check if a mod is server side.

    Args:
        project (dict): The project information from the Labrinth API.

    Returns:
        bool: True if the mod is server side, False otherwise.
    """
    if project["server_side"] == "required":
        return True
    return False


def main():
    """Extract server side mods from the Prominence pack."""
    directory = pathlib.Path(__file__).parent
    file_name = "prominence-pack.md"

    modrinth_client = LabrinthAPI()

    links = parse_markdown_links(directory, file_name)

    server_side_mods = []
    projects = modrinth_client.get_multiple_projects(list(links.keys()))

    for project in projects:
        if is_server_side_mod(project):
            print(f"{project['title']} is server side.")
            server_side_mods.append(project)
        else:
            print(f"{project['title']} is not server side.")

    # output the name of the mod and the URL for it
    server_mods = {}
    for mod in server_side_mods:
        server_mods[mod["title"]] = links[mod["slug"]]["url"]
    with open(directory / "server_mods.json", "w") as file:
        # Sort dict alphabetically by the name + ignoring case:
        server_mods = dict(sorted(server_mods.items(), key=lambda x: x[0].upper()))
        json.dump(server_mods, file, indent=4)


if __name__ == "__main__":
    main()
