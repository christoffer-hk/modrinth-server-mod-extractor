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
        res = self._session.get(url).json()
        return res

    def get_game_version_specific_project_version(self, id: str, game_version: str = "1.20.1") -> dict: ...

    # def get_projects(self, ids: list[str]) -> list[dict]:
    #     """Get multiple projects by their IDs."""
    #     url = f"{self.base_url}/projects"
    #     res = self._session.get(url, params={"ids": ids}).json()
    #     return res


if __name__ == "__main__":
    api = LabrinthAPI()
