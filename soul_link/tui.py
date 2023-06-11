import os
from threading import Thread

import pandas as pd
from colorama import Back, Style, init

from soul_link import keyboard


class TUI:
    _MODE_TABLE = "table"
    _MODE_ROW = "row"
    _MODE_COLUMN = "column"

    _CURSOR_UP = -1
    _CURSOR_DOWN = 1
    _CURSOR_LEFT = -1
    _CURSOR_RIGHT = 1
    _CURSOR_INITIAL_POS = (1, 0)

    # Used for scape secuences
    _CHAR_DIRECTION_UP = "A"
    _CHAR_DIRECTION_DOWN = "B"
    _CHAR_SCAPE = "\x1b"
    _CHAR_CTRL = "["
    _CHAR_HOME = "H"

    def __init__(self, dataframe: pd.DataFrame):
        self._dataframe: pd.DataFrame = dataframe
        self._cursor_line: int = 0
        self._cursor_column: int = 0
        self._bottom_index: int = 0
        self._top_index: int = 0
        self._terminal_size = ()
        self._view_data = None
        self._mode = self._MODE_TABLE
        init()

    def _display(self):
        """
        Print the main TUI interface containing the table. This function should be called the first time
        that interface should be displayed.
        """
        self._clear_console()
        self._update_terminal_size()
        self._update_view_data()
        self._calculate_columns_widths()

        print("|", end="")
        for column in self._dataframe.columns:
            print(f"{column: ^{self._column_widths[column]}}|", end="")
        print()
        self._cursor_line += 1

        for index, row in self._view_data.iterrows():
            select_row = False
            if self._mode == self._MODE_ROW and index == self._cursor_line:
                select_row = True
            select_col = False
            if self._mode == self._MODE_COLUMN:
                select_col = True
            self._print_row(row, select_row=select_row, select_col=select_col, reset_cursor_line=False)
        self._move_cursor_position(self._CURSOR_INITIAL_POS)

    def _read_keys(self):
        """
        Read keyboard key presses.
        """

        def move_line(direction: int):
            if self._mode == self._MODE_TABLE:
                self._print_row(self._view_data.iloc[self._cursor_line - 1], select_row=True)
            else:
                self._add_cursor_line(
                    direction,
                    pre_hook=self._print_row,
                    pre_hook_args=(self._view_data.iloc[self._cursor_line - 1], False, False),
                )
                self._print_row(self._view_data.iloc[self._cursor_line - 1], True, False)
            self._mode = self._MODE_ROW

        def move_column(direction):
            if self._mode == self._MODE_ROW:
                self._print_row(self._view_data.iloc[self._cursor_line - 1], select_col=True)
            if self._mode == self._MODE_COLUMN:
                if (self._cursor_column + direction) < 0:
                    self._cursor_column = len(self._view_data.columns) - 1
                elif (self._cursor_column + direction) > len(self._view_data.columns) - 1:
                    self._cursor_column = 0
                else:
                    self._cursor_column += direction
            self._print_row(self._view_data.iloc[self._cursor_line - 1], select_col=True)
            self._mode = self._MODE_COLUMN

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

        keyboard.read_keys(on_key_press=on_key_press)

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

    def _update_view_data(self):
        """
        Based on terminal size, create a smaller `pd.DataFrame` used to iterate over and display.
        """
        self._view_data = self._dataframe.iloc[self._top_index : self._terminal_size[0] - 1]
        self._bottom_index = len(self._view_data) - 1

    def _clear_console(self):
        """
        Clear shell console.
        """
        os.system("cls" if os.name == "nt" else "clear")

    def _calculate_columns_widths(self):
        """
        Based on column name length, calculate a width that properly fits the columns.
        """
        self._column_widths = {}
        for column in self._dataframe.columns:
            self._column_widths[column] = len(column) + 4

    def _print_row(
        self, data: pd.Series, select_row: bool = False, select_col: bool = False, reset_cursor_line: bool = True
    ):
        """
        Print a table row data from a `pd.DataFrame.iterrows()` `pd.Series`.

        Args:
            data (`pd.Series`): Data that should be printed.
            select_row (bool): Add background color to the row. Useful for selecting rows.
            move_cursor_line (bool): If `true`, move the cursor to the following line. If `False`, move the
                cursor to the beggining of the printed line.
        """
        row = "|"
        for i, column in enumerate(data.index):
            color = ""
            reset = ""
            if select_col and i == self._cursor_column:
                color = Back.LIGHTBLUE_EX
                reset = Style.RESET_ALL
            display_data = data[column]
            if len(data[column]) > self._column_widths[column]:
                display_data = f"{data[column][:self._column_widths[column] - 3]}..."
            row += f"{color}{display_data: ^{self._column_widths[column]}}{reset}|"

        if select_row or select_col:
            print(row, flush=True)
        else:
            print(f"{Style.DIM}{row}{Style.RESET_ALL}", flush=True)

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
        if self._cursor_line + add_line > len(self._view_data) or self._cursor_line + add_line <= 0:
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
                self._print_row(self._view_data.iloc[self._cursor_line - 1])
            case self._MODE_COLUMN:
                self._mode = self._MODE_ROW
                self._print_row(self._view_data.iloc[self._cursor_line - 1], select_row=True)
