import fcntl
import os
import struct
import termios
from threading import Thread

import pandas as pd
from colorama import Back, Fore, Style, init

from soul_link import keyboard


class TUI:
    _MODE_TABLE = "table"
    _MODE_ROW = "row"

    _CURSOR_UP = (-1, 0)
    _CURSOR_DOWN = (1, 0)
    _CURSOR_INITIAL_POS = (1, 0)

    _CHAR_DIRECTION_UP = "A"
    _CHAR_DIRECTION_DOWN = "B"

    def __init__(self, dataframe: pd.DataFrame):
        self._dataframe: pd.DataFrame = dataframe
        self._cursor_y: int = 0
        self._bottom_index: int = 0
        self._top_index: int = 0
        self._terminal_size = ()
        self._view_data = None
        self._mode = self._MODE_TABLE
        init()

    def _display(self):
        self._clear_console()
        self._update_terminal_size()
        self._update_view_data()
        self._calculate_columns_widths()

        print("|", end="")
        for column in self._dataframe.columns:
            print(f"{column: ^{self._column_widths[column]}}|", end="")
        print()
        self._cursor_y += 1

        for _, row in self._view_data.iterrows():
            self._print_row(row)
        self._move_cursor(self._CURSOR_INITIAL_POS)
        self._move_cursor(self._CURSOR_INITIAL_POS)

    def _event_loop(self):
        def on_key_press(key: str):
            match key:
                case keyboard.KEY_ARROW_UP:
                    if self._mode == self._MODE_TABLE:
                        self._mode = self._MODE_ROW
                        self._print_row(self._view_data.iloc[self._cursor_y], with_background=True, move_cursor=False)
                    else:
                        self._add_cursor(self._CURSOR_UP)
                case keyboard.KEY_ARROW_DOWN:
                    if self._mode == self._MODE_TABLE:
                        self._mode = self._MODE_ROW
                        self._print_row(self._view_data.iloc[self._cursor_y], with_background=True, move_cursor=False)
                    else:
                        self._add_cursor(self._CURSOR_DOWN)
                case keyboard.KEY_ESC:
                    self._exit_mode()

        keyboard.read_keys(on_key_press=on_key_press)

    def init_tui(self):
        # fd = sys.stdout.fileno()
        # set_winsize(fd, 10, 100)

        threads = []
        threads.append(Thread(target=self._event_loop))

        self._display()
        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def _update_terminal_size(self):
        size = os.get_terminal_size()
        self._terminal_size = (size.lines - 1, size.columns)

    def _update_view_data(self):
        self._view_data = self._dataframe.iloc[self._top_index : self._terminal_size[0] - 1]
        self._bottom_index = len(self._view_data) - 1

    def _clear_console(self):
        """
        Clear shell console.
        """
        os.system("cls" if os.name == "nt" else "clear")

    def _calculate_columns_widths(self):
        self._column_widths = {}
        for column in self._dataframe.columns:
            self._column_widths[column] = len(column) + 4

    def _print_row(self, data: pd.Series, with_background: bool = False, move_cursor: bool = True):
        row = "|"
        for column in data.index:
            row += f"{data[column]: ^{self._column_widths[column]}}|"

        if with_background:
            print(f"{Back.BLUE}{Fore.BLACK}{row}{Style.RESET_ALL}", flush=True)
        else:
            print(row, flush=True)

        if move_cursor:
            self._cursor_y += 1
        else:
            print("\x1b[1A", end="", flush=True)

    def _move_cursor(self, position: (int)):
        """
        Move cursor to given. Currently the cursor is just moved in the `y` axis.
        TODO: support `x` movement.
        TODO: check for out of bounds.

        Args:
            position ((int)): tuple with `y` and `x` positions where the cursor should be moved.
        """
        y, _ = position

        difference_y = self._cursor_y - y
        direction = self._CHAR_DIRECTION_UP
        if difference_y < 0:
            direction = self._CHAR_DIRECTION_DOWN
        elif difference_y == 0:
            return

        print(f"\x1b[{difference_y}{direction}", end="", flush=True)
        self._cursor_y = y - 1

    def _add_cursor(self, position: str):
        """
        Add position to current cursor position. Currently the cursor is just moved in the `y` axis.
        TODO: support `x` movement.
        TODO: check for out of bounds.

        Args:
            position ((int)): tuple with `y` and `x` positions that should be added to the current cursor position.
        """
        y, _ = position
        if self._cursor_y + y > len(self._view_data) - 1 or self._cursor_y + y < 0:
            return

        direction = self._CHAR_DIRECTION_DOWN
        if y < 0:
            direction = self._CHAR_DIRECTION_UP

        # re-print current line to remove background color
        self._print_row(self._view_data.iloc[self._cursor_y], with_background=False, move_cursor=False)
        print(f"\x1b[1{direction}", end="", flush=True)
        self._cursor_y += y
        self._print_row(self._view_data.iloc[self._cursor_y], with_background=True, move_cursor=False)

    def _exit_mode(self):
        match self._mode:
            case self._MODE_ROW:
                self._mode = self._MODE_TABLE
                self._print_row(self._view_data.iloc[self._cursor_y], move_cursor=False)


def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
