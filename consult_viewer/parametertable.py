import array
import enum

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Slot, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QAbstractItemView
from random import randrange
import consult_interface as consult

class ColumnId(enum.IntEnum):
    NAME = 0
    VALUE = 1
    UNITS = 2

class ConsultParameterTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._columns = ["Parameter Name", "Value", "Units"]
        self._params = consult.Definition.get_enabled_parameters()

    def rowCount(self, parent=QModelIndex()):
        count = consult.Definition.count_enabled_parameters()
        return count

    def columnCount(self, parent=QModelIndex()):
        count = len(self._columns)
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
            if index.column() == 0:
                return self._params[index.row()].name
            elif index.column() == 1:
                value = self._params[index.row()].get_value()
                if value is None:
                    return randrange(0, 100)
                return value
            elif index.column() == 2:
                return self._params[index.row()].unit_label
        return None

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def param_id_to_row(self, param_id):
        for i, param in enumerate(self._params):
            if param.id == param_id:
                return i
        return -1

    def parameters_changed(self):
        self.beginResetModel()
        self._params = consult.Definition.get_enabled_parameters()
        self.endResetModel()

    def update_value(self, parameter_id):
        param_row = self.param_id_to_row(parameter_id)
        if param_row != -1:
            self.dataChanged.emit(self.index(param_row, ColumnId.VALUE), self.index(param_row, ColumnId.VALUE))

    def update_values(self, parameter_ids=None):
        if parameter_ids is None:
            self.dataChanged.emit(self.index(0, ColumnId.VALUE), self.index(self.rowCount(), ColumnId.VALUE))
        else:
            for param_id in parameter_ids:
                self.update_value(param_id)


class ParameterTableView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self._table = QTableView(self)
        self._table.setContentsMargins(0, 0, 0, 0)

        # Create and populate the tableWidget
        # table.setItemDelegate(StarDelegate())
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._model = ConsultParameterTableModel()
        self._table.setModel(self._model)
        self._table.resizeColumnsToContents()
        layout.addWidget(self._table)
        self.setLayout(layout)

    @Slot()
    def parameters_changed(self):
        self._model.parameters_changed()
        self._table.resizeColumnsToContents()
