from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QAbstractItemView
from random import randrange
import consult_interface as consult


class ConsultParameterTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._params = consult.Definition.get_parameters()

        self.input_data = []
        self.mapping = {}
        self.column_count = 4
        self.row_count = len(self._params)

        for i in range(self.row_count):
            data_vec = [0] * self.column_count
            for k in range(len(data_vec)):
                if k % 2 == 0:
                    data_vec[k] = i * 50 + randrange(30)
                else:
                    data_vec[k] = randrange(100)
            self.input_data += data_vec

    def rowCount(self, parent=QModelIndex()):
        return len(self.input_data)

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            if section % 2 == 0:
                return "x"
            else:
                return "y"
        else:
            return str(section + 1)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self.input_data[index.row()][index.column()]
        elif role == Qt.ItemDataRole.EditRole:
            return self.input_data[index.row()][index.column()]
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            row = index.row()
            col = index.column()
            self.input_data[row][col] = float(value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable


class ParameterTableView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        table = QTableView(self)
        table.setContentsMargins(0, 0, 0, 0)

        # Create and populate the tableWidget
        # table.setItemDelegate(StarDelegate())
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # table.setModel(ConsultParameterTableModel())
        layout.addWidget(table)
        self.setLayout(layout)
