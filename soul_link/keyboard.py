import readkeys

KEY_ARROW_UP = "1b5b41"
KEY_ARROW_DOWN = "1b5b42"
KEY_ESC = "1b"
KEY_X = "78"
KEY_BACKSPACE = "7f"

COM_CTRL_D = "04"
COM_CTRL_C = "03"


def default_on_key_press(key: str):
    print(key)


def read_keys(on_key_press: callable = default_on_key_press, exit_key: str = COM_CTRL_C):
    key = ""
    while key != exit_key:
        key = readkeys.getkey().encode("utf-8").hex()
        on_key_press(key=key)
