from abc import ABC, abstractmethod


class EcuParam(ABC):
    def __init__(self, name, unit_label="", scale=1.0, offset=0.0):
        self.name = name
        self.unit_label = unit_label
        self.scale = scale
        self.offset = offset
        self.enabled = False

    @abstractmethod
    def get_registers(self) -> bytes:
        """
        Get the register bytes for this parameter, will be two bytes for dual parameters (MSB, LSB) and
        one byte for single parameters
        :return: the register bytes for this parameter
        """
        pass

    @abstractmethod
    # test
    def get_register(self) -> bytes:
        """
        Get the register for this parameter, guaranteed to be a single byte. LSB is used for dual parameters
        :return: the register byte for this parameter
        """
        pass

    @abstractmethod
    def get_unscaled_value(self, frame):
        pass

    def get_value(self, frame):
        return (self.get_unscaled_value(frame) * self.scale) + self.offset

    def enable(self, state=True):
        self.enabled = state


class EcuParamSingle(EcuParam):
    def __init__(self, name, register: bytes, unit_label="", scale=1, offset=0):
        super().__init__(name, unit_label, scale, offset)
        self.register = register

    def get_registers(self) -> bytes:
        return self.get_register()

    def get_register(self) -> bytes:
        return bytes(self.register)

    def get_unscaled_value(self, frame):
        return frame[self.register]


class EcuParamDual(EcuParam):
    def __init__(self, name, register_msb: bytes, register_lsb: bytes, unit_label="", scale=1, offset=0):
        super().__init__(name, unit_label, scale, offset)
        self.register_msb = register_msb
        self.register_lsb = register_lsb

    def get_registers(self) -> bytes:
        both = self.register_msb + self.register_lsb
        return bytes(both)

    def get_register(self) -> bytes:
        return bytes(self.register)

    def get_unscaled_value(self, frame):
        return (frame[self.register_msb] << 8) + frame[self.register_lsb]


class EcuParamBit(EcuParam):
    def __init__(self, name, register: bytes, bit, unit_label="", scale=1, offset=0):
        super().__init__(name, unit_label, scale, offset)
        self.register = register
        self.bit = bit

    def get_registers(self) -> bytes:
        return self.get_register()

    def get_register(self) -> bytes:
        return bytes(self.register)

    def get_unscaled_value(self, frame):
        return (frame[self.register] >> self.bit) & 1
