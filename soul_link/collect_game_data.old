from soul_link.wrappers.steam import get_app_details, get_app_id_from_store_url


def collect_steam_game_data(url: str) -> dict:
    """
    Get Steam game store details.

    Args:
        url (str): URL where the Steam application ID will be gathered to collect game data.

    Returns:
        dict: the dictionary has the following keys:
            - name (str): Game name.
            - is_free (bool): `true` if the game is free, `false` otherwise.
            - short_description (str): Steam game short description.
            - categories (list[str]): list of game categories like `Single-Player`.
            - genres (list[str]): list of game genres like 'Strategy'.
            - release (bool): `true` if the game has been releashed, `false` otherwise.

    Raises:
        wrappers.steam.SteamInvalidStoreURL: Raised if the given `url` is not a valid Steam store URL.
        wrappers.steam.SteamInvalidAppID: Raised if the given `app_id` is not a valida number or equal or less than 0.
        requests.exceptions.ConnectionError: If the connection to steam can not be stablished.
    """
    if not url.startswith("https://store.steampowered.com"):
        print("Currently we only support Steam store URLs")

    app_id = str(get_app_id_from_store_url(url))
    app_details = get_app_details(app_id)

    if app_id not in app_details or not app_details[app_id]["success"]:
        print("Game does not exist")
        return

    app_details = app_details[app_id]
    return_details = {}
    return_details["name"] = app_details["data"]["name"]
    return_details["is_free"] = app_details["data"]["is_free"]
    return_details["short_description"] = app_details["data"]["short_description"]

    return_details["categories"] = []
    for category in app_details["data"]["categories"]:
        return_details["categories"].append(category["description"])

    return_details["genres"] = []
    for genre in app_details["data"]["genres"]:
        return_details["genres"].append(genre["description"])

    return_details["released"] = False
    if (
        "comin_soon" not in app_details["data"]["release_date"]
        and not app_details["data"]["release_date"]["coming_soon"]
    ):
        return_details["released"] = True
    return return_details
