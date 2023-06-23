import gspread
import numpy as np


class SheetWrapper:
    def __init__(self, sheet: gspread.Spreadsheet):
        self._sheet = sheet

    def get_array(self) -> np.ndarray:
        return np.array(self._sheet.get_worksheet(0).get_all_values())

    def update_sheet(self, data: np.ndarray):
        self._sheet.get_worksheet(0).update(data.tolist())
