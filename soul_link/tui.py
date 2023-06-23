import os
from threading import Lock, Thread

import numpy as np
from colorama import Back, Style, init

from soul_link import keyboard


class TUI:
    _MODE_TABLE = "table"
    _MODE_ROW = "row"
    _MODE_COLUMN = "column"

    _EXIT_KEYS = (keyboard.COM_CTRL_C, keyboard.COM_CTRL_D)

    _CURSOR_UP = -1
    _CURSOR_DOWN = 1
    _CURSOR_LEFT = -1
    _CURSOR_RIGHT = 1
    _CURSOR_INITIAL_POS = (1, 0)

    # Used for scape sequences
    _CHAR_DIRECTION_UP = "A"
    _CHAR_DIRECTION_DOWN = "B"
    _CHAR_SCAPE = "\x1b"
    _CHAR_CTRL = "["
    _CHAR_HOME = "H"

    def __init__(self, data: np.ndarray, on_data_update: callable):
        self._data: np.ndarray = data
        self._on_data_update: callable = on_data_update
        self._cursor_line: int = 1
        self._cursor_column: int = 0
        self._top_index: int = 1
        self._data
        self._bottom_index: int = self._data.shape[0]
        self._terminal_size = ()
        self._mode = self._MODE_TABLE
        init()

    def _display(self):
        """
        Print the main TUI interface containing the table. This function should be called the first time
        that interface should be displayed.
        """
        self._clear_console()
        self._update_terminal_size()
        self._calculate_columns_widths()

        self._print_row(self._data[0], select_row=True, reset_cursor_line=False)
        for i, row in enumerate(self._data[self._top_index : self._bottom_index], start=1):
            select_row = False
            if self._mode == self._MODE_ROW and i == self._cursor_line:
                select_row = True
            select_col = False
            if self._mode == self._MODE_COLUMN:
                select_col = True
            self._print_row(row, select_row=select_row, select_col=select_col, reset_cursor_line=False)
        self._move_cursor_position((self._cursor_line, 0))

    def _read_keys(self):
        """
        Read keyboard key presses.
        """
        lock = Lock()

        def move_line(direction: int):
            with lock:
                if self._mode == self._MODE_TABLE:
                    self._print_row(self._data[self._cursor_line], select_row=True)
                else:
                    self._add_cursor_line(
                        direction,
                        pre_hook=self._print_row,
                        pre_hook_args=(self._data[self._cursor_line], False, False),
                    )
                    self._print_row(self._data[self._cursor_line], True, False)
                self._mode = self._MODE_ROW

        def move_column(direction: int):
            with lock:
                if self._mode == self._MODE_ROW:
                    self._print_row(self._data[self._cursor_line], select_col=True)
                if self._mode == self._MODE_COLUMN:
                    if (self._cursor_column + direction) < 0:
                        self._cursor_column = len(self._data[0]) - 1
                    elif (self._cursor_column + direction) > len(self._data[0]) - 1:
                        self._cursor_column = 0
                    else:
                        self._cursor_column += direction
                self._print_row(self._data[self._cursor_line], select_col=True)
                self._mode = self._MODE_COLUMN

        def delete_row():
            with lock:
                self._data = np.delete(self._data, self._cursor_line, axis=0)
                self._display()
            self._on_data_update(self._data)

        def on_key_press(key: str):
            match key:
                case keyboard.KEY_ARROW_UP:
                    move_line(self._CURSOR_UP)
                case keyboard.KEY_ARROW_DOWN:
                    move_line(self._CURSOR_DOWN)
                case keyboard.KEY_ARROW_LEFT:
                    move_column(self._CURSOR_LEFT)
                case keyboard.KEY_ARROW_RIGHT:
                    move_column(self._CURSOR_RIGHT)
                case keyboard.KEY_ESC:
                    self._exit_mode()
                case keyboard.KEY_X:
                    if self._mode == self._MODE_TABLE:
                        return False
                case keyboard.KEY_BACKSPACE:
                    if self._mode == self._MODE_ROW:
                        delete_row()
            return True

        keyboard.read_keys(on_key_press=on_key_press, exit_keys=self._EXIT_KEYS)

    def init_tui(self):
        """
        Initialize the text user interface.
        """
        threads = []
        threads.append(Thread(target=self._read_keys))

        self._display()
        for t in threads:
            t.start()

        for t in threads:
            t.join()

    def _update_terminal_size(self):
        """
        Get ther terminal size to avoid having more lines that can be displayed.
        """
        size = os.get_terminal_size()
        self._terminal_size = (size.lines - 1, size.columns)

    def _clear_console(self):
        """
        Clear shell console.
        """
        os.system("cls" if os.name == "nt" else "clear")

    def _calculate_columns_widths(self):
        """
        Based on column name length, calculate a width that properly fits the columns.
        """
        self._column_widths = []
        for column in self._data[0]:
            self._column_widths.append(len(column) + 4)

    def _print_row(
        self,
        row: np.ndarray,
        select_row: bool = False,
        select_col: bool = False,
        reset_cursor_line: bool = True,
    ):
        """
        Print a table row data from a `pd.DataFrame.iterrows()` `pd.Series`.

        Args:
            row (`np.ndarray`): Row that needs to be printed.
            select_row (bool): Add style `colorama.Style.DIM` to printed row. Useful for selecting rows.
            select_col (bool): Add background color `colorama.Back.LIGHTBLUE_EX` to printed col. Useful for selecting
            cols.
            move_cursor_line (bool): If `true`, move the cursor to the following line. If `False`, move the
            cursor to the beggining of the printed line.
        """
        row_str = "|"
        for i, column in enumerate(row):
            color = ""
            reset = ""
            if select_col and i == self._cursor_column:
                color = Back.LIGHTBLUE_EX
                reset = Style.RESET_ALL
            display_data = column
            if len(column) > self._column_widths[i]:
                display_data = f"{column[:self._column_widths[i] - 3]}..."
            row_str += f"{color}{display_data: ^{self._column_widths[i]}}{reset}|"

        if select_row or select_col:
            print(row_str, flush=True)
        else:
            print(f"{Style.DIM}{row_str}{Style.RESET_ALL}", flush=True)

        if reset_cursor_line:
            print(f"{self._CHAR_SCAPE}{self._CHAR_CTRL}1A", end="", flush=True)

    def _move_cursor_position(self, position: (int)):
        """
        Move cursor to given.

        Args:
            position ((int)): tuple with `y` and `x` positions where the cursor should be moved.
        """
        y, x = position

        if y < 0 or x < 0:
            return
        print(f"{self._CHAR_SCAPE}{self._CHAR_CTRL}{y};{x}{self._CHAR_HOME}")

    def _add_cursor_line(
        self,
        add_line: int,
        pre_hook: callable,
        pre_hook_args: tuple() = (),
    ):
        """
        Add position to current cursor line position.

        Args:
            add_line (int): lines that should be add to the current line position.
            pre_hook: (callable): function that should be called if the position could be added.
            pre_hook_args (tuple): tuple with `pre_hook` function arguments.
        """
        if self._cursor_line + add_line > self._data.shape[0] or self._cursor_line + add_line <= 0:
            return

        direction = self._CHAR_DIRECTION_DOWN
        if add_line < 0:
            direction = self._CHAR_DIRECTION_UP

        # re-print current line to remove background color
        if pre_hook:
            pre_hook(*pre_hook_args)
        print(f"{self._CHAR_SCAPE}{self._CHAR_CTRL}1{direction}", end="", flush=True)
        self._cursor_line += add_line

    def _exit_mode(self):
        """
        Call this function to properly exit current mode.
        If the current mode is `TUI._MODE_ROW`, re-print the current cursor row without background while keeping
        the cursor on the same position.
        """
        match self._mode:
            case self._MODE_ROW:
                self._mode = self._MODE_TABLE
                self._print_row(self._data[self._cursor_line])
            case self._MODE_COLUMN:
                self._mode = self._MODE_ROW
                self._print_row(self._data[self._cursor_line], select_row=True)
