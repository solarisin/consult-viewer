from abc import ABC, abstractmethod
from random import randrange

from PySide6.QtCore import Qt, QModelIndex, QAbstractTableModel
from PySide6.QtGui import QColor


class EcuParam(ABC):
    def __init__(self, name, unit_label="", scale=1.0, offset=0.0):
        self.name = name
        self.unit_label = unit_label
        self.scale = scale
        self.offset = offset
        self.enabled = False

    @abstractmethod
    def get_registers(self):
        pass

    @abstractmethod
    def get_unscaled_value(self, frame):
        pass

    def get_value(self, frame):
        return (self.get_unscaled_value(frame) * self.scale) + self.offset

    def enable(self, state=True):
        self.enabled = state


class EcuParamSingle(EcuParam):
    def __init__(self, name, register, unit_label="", scale=1, offset=0):
        super().__init__(name, unit_label, scale, offset)
        self.register = register

    def get_registers(self):
        return [self.register]

    def get_unscaled_value(self, frame):
        return frame[self.register]


class EcuParamDual(EcuParam):
    def __init__(self, name, register_msb, register_lsb, unit_label="", scale=1, offset=0):
        super().__init__(name, unit_label, scale, offset)
        self.register_msb = register_msb
        self.register_lsb = register_lsb

    def get_registers(self):
        return [self.register_msb, self.register_lsb]

    def get_unscaled_value(self, frame):
        return (frame[self.register_msb] << 8) + frame[self.register_lsb]


class EcuParamBit(EcuParam):
    def __init__(self, name, register, bit, unit_label="", scale=1, offset=0):
        super().__init__(name, unit_label, scale, offset)
        self.register = register
        self.bit = bit

    def get_registers(self):
        return [self.register]

    def get_unscaled_value(self, frame):
        return (frame[self.register] >> self.bit) & 1


class ConsultModel:
    def __init__(self):
        self.init = '\xFF\xFF\xEF'
        self.init_response = '\x10'
        self.register_param = '\x5A' # prefixed before any register value
        self.start_stream = '\xF0' # terminates registration of values
        # ex: \x5A\x0B\x5A\x01 -> sets requested registers to '\x0B' and '\x01' (vehicle speed and engine speed),
        # then instructs the ECU to start streaming data
        self.stop_stream = '\x30'
        self.stop_ack = '\xCF'

        # params
        self.params = [
            EcuParamDual("Engine Speed HR", '\x00', '\x01', "RPM", 12.5),
            EcuParamDual("Engine Speed LR", '\x02', '\x03', "RPM", 8),
            EcuParamDual("MAF Voltage", '\x04', '\x05', "mV", 5),
            EcuParamDual("MAF Voltage RH", '\x04', '\x05', "mV", 5),
            EcuParamSingle("Coolant Temp", '\x08', "C", offset=-50),
            EcuParamSingle("O2 Voltage LH", '\x09', "mV", 10),
            EcuParamSingle("O2 Voltage RH", '\x0A', "mV", 10),
            EcuParamSingle("Vehicle Speed", '\x0B', "km/h", 2),
            EcuParamSingle("Battery Voltage", '\x0C', "V", 80),
            EcuParamSingle("TPS", '\x0D', "%", 20),
            EcuParamSingle("Fuel Temp", '\x0F', "C", offset=-50),
            EcuParamSingle("IAT", '\x11', "C", offset=-50),
            EcuParamSingle("EGT", '\x12', "mV", 20),
            EcuParamDual("Injector Time LH", '\x14', '\x15', "ms", 1/100),
            EcuParamSingle("Ignition Timing", '\x16', "deg BTDC", -1, 110),
            EcuParamSingle("AAC Valve", '\x17', "%", 1/2),
            EcuParamSingle("AF Alpha LH", '\x1A', "%"),
            EcuParamSingle("AF Alpha RH", '\x1B', "%"),
            EcuParamSingle("AF Alpha Selflearn LH", '\x1C', "%"),
            EcuParamSingle("AF Alpha Selflearn RH", '\x1D', "%"),
            EcuParamDual("Injector Time RH", '\x22', '\x23', "ms", 1/100),
            EcuParamSingle("Purge Valve Step", '\x25', "steps"),
            EcuParamSingle("Tank Fuel Temp", '\x26'),
            EcuParamSingle("FPCM Voltage", '\x27', "V"),
            EcuParamSingle("WG Solenoid", '\x28'),
            EcuParamSingle("Boost Voltage", '\x29', "V"),
            EcuParamSingle("Engine Mount", '\x2A'),
            EcuParamSingle("Position Counter", '\x2E'),
            EcuParamSingle("Fuel Gauge Voltage", '\x2F', "V"),
            EcuParamSingle("O2 Front B1 Voltage", '\x30', "V"),
            EcuParamSingle("O2 Front B2 Voltage", '\x31', "V"),
            EcuParamSingle("Ignition Switch", '\x32'),
            EcuParamSingle("CAL LD Value", '\x33'),
            EcuParamSingle("Fuel Schedule", '\x34'),
            EcuParamSingle("O2 Rear B1 Voltage", '\x35', "V"),
            EcuParamSingle("O2 Rear B2 Voltage", '\x36', "V"),
            EcuParamSingle("Throttle Position ABS", '\x37', "%"),
            EcuParamSingle("MAF Scaled", '\x38', "g/s"),
            EcuParamSingle("Evap Pressure Voltage", '\x39', "V"),
            EcuParamSingle("ABS Pressure Voltage A", '\x3A', "V"),
            EcuParamSingle("ABS Pressure Voltage B", '\x4A', "V"),
            EcuParamSingle("FPCM Pressure Voltage A", '\x52', "V"),
            EcuParamSingle("FPCM Pressure Voltage B", '\x53', "V"),
            EcuParamBit("A/C On", '\x13', 4),
            EcuParamBit("Power Steering", '\x13', 3),
            EcuParamBit("Park/Neutral", '\x13', 2),
            EcuParamBit("Cranking", '\x13', 1),
            EcuParamBit("CLSD/THL POS", '\x13', 0),
            EcuParamBit("A/C Relay", '\x1e', 7),
            EcuParamBit("Fuel Pump Relay", '\x1e', 6),
            EcuParamBit("VTC Solenoid", '\x1e', 5),
            EcuParamBit("Coolant Fan Hi", '\x1e', 1),
            EcuParamBit("Coolant Fan Lo", '\x1e', 0),
            EcuParamBit("P/Reg control valve", '\x1f', 6),
            EcuParamBit("WG Solenoid", '\x1f', 5),
            EcuParamBit("IACV FICD Solenoid", '\x1f', 3),
            EcuParamBit("EGR Solenoid", '\x1f', 0),
            EcuParamBit("LH Bank Lean", '\x21', 7),
            EcuParamBit("RH Bank Lean", '\x21', 6)]

    def get_params(self) -> list[EcuParam]:
        return self.params


ConsultInfo = ConsultModel()


class ConsultParameterTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._params = ConsultInfo.get_params()

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
            self.input_data.append(data_vec)

    def rowCount(self, parent=QModelIndex()):
        return len(self.input_data)

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    def headerData(self, section: int, orientation: Qt.Orientation, role: int=...):
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
        # elif role == Qt.ItemDataRole.BackgroundRole:
        #     for color, rect in self.mapping.items():
        #         if rect.contains(index.column(), index.row()):
        #             return QColor(color)
        #     # cell not mapped return white color
        #     return QColor(Qt.GlobalColor.white)
        return None

    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if index.isValid() and role == Qt.ItemDataRole.EditRole:
            self.input_data[index.row()][index.column()] = float(value)
            self.dataChanged.emit(index, index)
            return True
        return False

    def flags(self, index):
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable

    # def add_mapping(self, color, area):
    #     self.mapping[color] = area
    #
    # def clear_mapping(self):
    #     self.mapping = {}
