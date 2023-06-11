import readkeys

KEY_ARROW_UP = "1b5b41"
KEY_ARROW_DOWN = "1b5b42"
KEY_ARROW_RIGHT = "1b5b43"
KEY_ARROW_LEFT = "1b5b44"
KEY_ESC = "1b"
KEY_X = "78"
KEY_BACKSPACE = "7f"

COM_CTRL_D = "04"
COM_CTRL_C = "03"


def _default_on_key_press(key: str) -> bool:
    """
    Default function for `soul_link.keyboard.read_keys` `on_key_press` arg. Prints the given key. Refer for the
    docstring of `soul_link.keyboard.read_keys` for further information on this function usge and replacement.
    """
    print(key)
    return True


def read_keys(on_key_press: callable = _default_on_key_press, exit_keys: tuple[str] = (COM_CTRL_C,)):
    """
    Read full stdin ANSI scape sequences. This even reads the full sequence of arrow keys.

    Args:
        on_key_press (callable): Function that should be called when a new key press is detected. If this argument is
            null, the function `soul_link.keyboard._default_on_key_press` will be called.
            This is the `on_key_press` docstring:
            '''
            Function called when a new key press is detected:

            Args:
                key (str): hexadecimal `str` representation of the ANSI scape sequence.

            Returns:
                bool: if `False`, the function `soul_link.keyboard.read_keys` will terminate.
            '''
        exit_keys (tuple[str]): tuple of ANSI sequences representations of keys that will make this function terminate
            if pressed. Defaults to `(COM_CTRL_C,)`.
    """
    key = ""
    while key not in exit_keys:
        key = readkeys.getkey().encode("utf-8").hex()
        if not on_key_press(key=key):
            break
