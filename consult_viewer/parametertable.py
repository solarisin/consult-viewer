import array

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QAbstractItemView
from random import randrange
import consult_interface as consult


class ConsultParameterTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._columns = ["Parameter Name", "Value", "Units"]
        self._params = consult.Definition.get_enabled_parameters()

    def rowCount(self, parent=QModelIndex()):
        count = consult.Definition.count_enabled_parameters()
        print("row count: ", count)
        return count

    def columnCount(self, parent=QModelIndex()):
        count = len(self._columns)
        print("column count: ", count)
        return len(self._columns)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            return self._columns[section]
        else:
            return str(section + 1)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            print("data: ", index.row(), index.column())
            if index.column() == 0:
                return self._params[index.row()].name
            elif index.column() == 1:
                return randrange(0, 100)
            elif index.column() == 2:
                return self._params[index.row()].units
        return None

    # def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
    #     if index.isValid() and role == Qt.ItemDataRole.EditRole:
    #         row = index.row()
    #         col = index.column()
    #         self.input_data[row][col] = float(value)
    #         self.dataChanged.emit(index, index)
    #         return True
    #     return False

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
        # return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable


# TODO cant do it this easily - need to keep a local list and determine how many rows were added/removed and override
#  beginInsertRows and beginRemoveRows in addRow and removeRow
    def refresh(self):
        self.dataChanged.emit(self.index(0, 0), self.index(self.rowCount(), self.columnCount()))


class ParameterTableView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        table = QTableView(self)
        table.setContentsMargins(0, 0, 0, 0)

        # Create and populate the tableWidget
        # table.setItemDelegate(StarDelegate())
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._model = ConsultParameterTableModel()
        table.setModel(self._model)
        layout.addWidget(table)
        self.setLayout(layout)

    @Slot()
    def update_data(self):
        print("in update_data slot")
        self._model.refresh()
