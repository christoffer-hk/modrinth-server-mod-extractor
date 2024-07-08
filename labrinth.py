"""API Client for the Labrinth (modrinth) API."""

import os

import requests

USER_AGENT = os.getenv("USER_AGENT")


class LabrinthAPI:
    """API Client for the Labrinth (modrinth) API.

    Allows us to retrieve information about mods (projects) from the Labrinth API.
    """

    test_url = "https://staging-api.modrinth.com/"
    base_url = "https://api.modrinth.com"

    def __init__(self):
        """Initialize the Labrinth API client.

        Check if we can connect to the API and set the base URL with latest major version.
        """
        res = requests.get(self.test_url).json()

        if res["about"] != "Welcome traveler!":
            raise Exception("Failed to connect to the Labrinth API.")

        self.version = res["version"].split(".")[0]
        self.base_url = f"{self.base_url}/v{self.version}"

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": USER_AGENT})

    def get_project(self, id: str) -> dict:
        """Get a project by its ID."""
        url = f"{self.base_url}/project/{id}"

        data = self._session.get(url)
        data.raise_for_status()

        res = data.json()
        return res

    def get_multiple_projects(self, project_list: list[str]) -> list[dict]:
        """Get multiple projects at once."""
        url = f"{self.base_url}/projects"

        # Note: Inside the [] we need each mod name
        # to have a double quote around them, comma separated for it to work
        params = {"ids": '["' + '","'.join(project_list) + '"]'}

        res = self._session.get(url, params=params)
        res.raise_for_status()

        json = res.json()
        return json

    def get_project_version_download_url(
        self,
        project_id: str,
        loader: str | None = None,
        game_version: str | None = None,
        featured: bool | None = None,
    ):
        """Get the download URL for a project version.

        Args:
            project_id (str): The ID of the project.
            loader (str, optional): The loader of the project. Example: "fabric", "forge".
            game_version (str, optional): The game version of the project. Example: "1.19.3", "1.20.1".
            featured (bool, optional): Whether the project is featured. Allowed: True, False.
        """
        url = f"{self.base_url}/project/{project_id}/version"

        # Construct query parameters
        params = {
            "loaders": f'["{loader}"]' if loader else None,
            "game_versions": f'["{game_version}"]' if game_version else None,
            "featured": str(featured).lower() if featured is not None else None,
        }

        # Filter out None values
        params = {k: v for k, v in params.items() if v is not None}

        res = self._session.get(url, params=params)

        if res.status_code != 200:
            raise Exception("Failed to get download URL")
        json = res.json()
        if json is None or len(json) == 0 or json[0].get("files") is None:
            raise Exception(f"No download URL found for project {project_id}")

        download_url = json[0]["files"][0]["url"]
        return download_url


if __name__ == "__main__":
    api = LabrinthAPI()
