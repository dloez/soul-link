import json
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

import gspread

from soul_link.data import SheetWrapper
from soul_link.tui import TUI

DEFAULT_SERVICE_ACCOUNT_FILE_PATH = "./service_account.json"
ENV_VAR_SEVICE_ACCOUNT_FILE_PATH = "SOUL_SERVICE_ACCOUNT"
USER_DATA = "~/.config/soulink/user.data"

DEFAULT_SHEET_HEADER = ["name", "is_free", "short_description", "categories", "genres", "released"]


def get_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("list", type=str, help="Game list name.")
    return parser


def get_service_account_cred_file_path() -> Path | None:
    """
    Retrive the path for the `service_account.json` file. It is searched by:
        1. From the working directory in the file `service_account.json`.
        2. From the environment variable defined in `ENV_VAR_SEVICE_ACCOUNT_FILE_PATH`. This variable
        should have a relative or absolute path to the json file containing the service account
        credentials information.

    Returns:
        Path pointing to the service account credentials file.
        None if the file is missing.
    """
    default_path = Path(DEFAULT_SERVICE_ACCOUNT_FILE_PATH)
    if default_path.exists():
        return default_path

    env_var_path = os.environ.get(ENV_VAR_SEVICE_ACCOUNT_FILE_PATH, "")
    if env_var_path:
        env_var_path = Path(env_var_path)
        if env_var_path.exists():
            return env_var_path
    return None


def load_user_data() -> dict:
    """
    Load user data from `USER_DATA` file.

    Returns:
        dict with the json contained by `user.data` file.
    """
    user_data_path = Path(USER_DATA).expanduser()
    user_data_path.parent.mkdir(parents=True, exist_ok=True)

    if not user_data_path.exists():
        with open(user_data_path, "w") as handler:
            handler.write("{}")
            return {}

    with open(user_data_path, "r") as handler:
        return json.load(handler)


def write_user_data(user_data: dict):
    """
    Write user data to `USER_DATA` file.

    Args:
        dict that will be written to `user.data` file.
    """
    with open(Path(USER_DATA).expanduser(), "w") as handler:
        json.dump(user_data, handler)


def create_default_sheet(gc: gspread.client.Client, sheet_title: str) -> gspread.Spreadsheet:
    """
    Create sheet with the given title.

    Args:
        sheet_title (str): Sheet title.

    Returns:
        gspread.Spreadsheet: created Sheet.
    """
    user_input = ""
    while not user_input:
        user_input = input("Enter your Google email: ")
    sheet = gc.create(sheet_title)
    res = sheet.share(email_address=user_input, perm_type="user", role="writer", notify=True)
    permissionId = res.json()["id"]
    sheet.transfer_ownership(permissionId)

    worksheet = sheet.get_worksheet(0)
    for i, header in enumerate(DEFAULT_SHEET_HEADER, start=1):
        worksheet.update_cell(1, i, header)
    print(f"Sheet created and tranferred to {user_input}!")


def main() -> int:
    """Main function."""
    parser = get_parser()
    args = parser.parse_args()

    service_account_creds = get_service_account_cred_file_path()
    if not service_account_creds:
        print(
            "Missing service account credentials. Please place the file `service_account.json` in the current",
            f"directory or define the environment variable {ENV_VAR_SEVICE_ACCOUNT_FILE_PATH} pointing to the file.",
        )
        return 1
    gc = gspread.service_account(filename=service_account_creds)

    user_data = load_user_data()
    if args.list not in user_data:
        user_data[args.list] = {}
        print(f"Creating new list '{args.list}'")
        user_data[args.list]["title"] = input(f"Google Sheet title [{args.list}]: ") or args.list
        write_user_data(user_data)

    sheet_title = user_data[args.list]["title"]
    try:
        sheet = gc.open(sheet_title)
    except gspread.SpreadsheetNotFound:
        print(f"There is not Google sheet with the title {sheet_title}!")
        print(f"Creating sheet {sheet_title}...")
        sheet = create_default_sheet(gc, sheet_title)

    sheet = gc.open(user_data[args.list]["title"])
    sheet_wrapper = SheetWrapper(sheet)

    tui = TUI(sheet_wrapper.get_array(), on_data_update=sheet_wrapper.update_sheet)
    tui.init_tui()
    return 0


if __name__ == "__main__":
    sys.exit(main())
