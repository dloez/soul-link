import re

import requests


def get_app_details(app_id: int | str, language: str = "en"):
    """
    Get Steam application shop details. In the documentation it is displayed that `appids` is a comma-separated
    list of application IDs but this is not working anymore, this is the reasson behind having `app_id` instead
    of `app_ids`.
    More information: https://github.com/Revadike/InternalSteamWebAPI/wiki/Get-App-Details

    Args:
        app_id (int | str): Steam application ID.
        language (str): Two character string representing the language for the response.

    Returns:
        dict: Response from  the REST API.

    Raises:
        wrappers.steam.SteamInvalidAppID: Raised if the given `app_id` is not a valida number or equal or less than 0.
        requests.exceptions.ConnectionError: If the connection to steam can not be stablished.
    """
    _validate_app_str_id(app_id)
    app_id = int(app_id)
    return requests.get(f"{STORE_API_BASE_URL}/appdetails?appids={app_id}&l={language}").json()


def get_app_id_from_store_url(url: str) -> int:
    """
    Extract the application ID from a Steam store URL.

    Args:
        url (str): Steam Store URL.

    Returns:
        int with the extracted application ID.

    Raises:
        wrappers.steam.SteamInvalidStoreURL: Raised if the given `url` is not a valid Steam store URL.
        wrappers.steam.SteamInvalidAppID: Raised if the given `app_id` is not a valida number or equal or less than 0.
    """
    if not re.search(STORE_URL_PATTERN, url):
        raise SteamInvalidStoreURL(url)

    str_id = url.split("/")[4]
    _validate_app_str_id(str_id)
    return int(str_id)


def _validate_app_str_id(app_id: str | int):
    """
    Validate if the given `app_id` is valid.

    Args:
        app_id (int | str): Steam application ID.

    Raises:
        wrappers.steam.SteamInvalidAppID: Raised if the given `app_id` is not a valida number or equal or less than 0.
    """
    if isinstance(app_id, str):
        found_chars = re.search("\D", app_id)
        if found_chars:
            raise SteamInvalidAppID(app_id)
        app_id = int(app_id)

    if app_id <= 0:
        raise SteamInvalidAppID(f"{app_id}")


class SteamInvalidAppID(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}. Steam application IDs have to be a number greater than 0."


class SteamInvalidStoreURL(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f"{self.message}. Steam store URLs need to conform the pattern '{STORE_URL_PATTERN}'."


STORE_API_BASE_URL = "https://store.steampowered.com/api"
STORE_URL_PATTERN = "^https:\/\/store.steampowered.com\/app\/.*[0-9]\/"
