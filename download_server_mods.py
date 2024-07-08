import json
import os
import pathlib
from time import sleep

import requests

from labrinth import LabrinthAPI

DOWNLOAD_FOLDER = pathlib.Path(__file__).parent / ".download"
GAME_VERSION = "1.20.1"
LOADER = "fabric"

client = LabrinthAPI()


def download_file(url: str, to_folder: pathlib.Path = DOWNLOAD_FOLDER):
    """Download a file from the Labrinth API."""
    if not os.path.exists(to_folder):
        try:
            os.mkdir(to_folder)
        except OSError as error:
            print(f"Failed to create {to_folder}: {error}")
            return False

    # Download file
    filename = url.split("/")[-1]
    filepath = os.path.join(to_folder, filename)
    # if file already exists, skip download
    if os.path.exists(filepath):
        print(f"{filename} already exists. Skipping download.")
        return True
    with open(filepath, "wb") as file:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        for chunk in response.iter_content(8192):
            file.write(chunk)
            file.flush()
    return True


def main():
    """Download server side mods from the Prominence pack."""
    directory = pathlib.Path(__file__).parent
    file_name = "server_mods.json"

    server_mods = {}
    with open(directory / file_name, "r") as file:
        server_mods = json.load(file)

    download_count = 0
    failed_mods = []
    for mod in server_mods.items():
        print(f"Downloading {mod[0]}... ({download_count+1}/{len(server_mods)})")
        try:
            url = client.get_project_version_download_url(
                mod[1].split("/")[-1],
                loader=LOADER,
                game_version=GAME_VERSION,
            )
        except Exception as error:
            print(error)
            continue

        try:
            download_file(url=url)
        except Exception as error:
            print(f"Failed to download {mod[0]}: {error}")
            failed_mods.append(mod)
            continue

        download_count += 1

        sleep(1)  # sleep for 1 second between downloads to reduce API load

    print("Download complete! \nDownloaded " f"{download_count}/{len(server_mods)} mods.")
    if failed_mods:
        print(f"Failed to download the following {len(failed_mods)} mod{'s' if len(failed_mods) > 1 else ''}:")
        for mod in failed_mods:
            print(f"{mod[0]} ({mod[1]})")


if __name__ == "__main__":
    main()
