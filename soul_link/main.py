from soul_link.wrappers.steam import get_app_details, get_app_id_from_store_url


def main():
    if not URL.startswith("https://store.steampowered.com"):
        print("Currently we only support Steam store URLs")

    app_id = str(get_app_id_from_store_url(URL))
    app_details = get_app_details(app_id)

    if app_id not in app_details or not app_details[app_id]["success"]:
        print("Game does not exist")
        return

    app_details = app_details[app_id]
    name = app_details["data"]["name"]
    is_free = app_details["data"]["is_free"]
    short_description = app_details["data"]["short_description"]

    categories = []
    for category in app_details["data"]["categories"]:
        categories.append(category["description"])

    genres = []
    for genre in app_details["data"]["genres"]:
        genres.append(genre["description"])

    released = False
    if (
        "comin_soon" not in app_details["data"]["release_date"]
        and not app_details["data"]["release_date"]["coming_soon"]
    ):
        released = True

    print(name, is_free, short_description, categories, genres, released, sep="\n")


if __name__ == "__main__":
    main()

URL = "https://store.steampowered.com/app/2190400/Toads_of_the_Bayou/"
