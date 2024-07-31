from .params import EcuParam, EcuParamSingle, EcuParamDual, EcuParamBit


class ConsultDefinition:
    def __init__(self):
        self.init = b'\xFF\xFF\xEF'
        self.init_response = b'\x10'
        # flag to be prefixed before any register value
        self.register_param = b'\x5A'
        # terminates registration of values
        self.start_stream = b'\xF0'
        # ex: \x5A\x0B\x5A\x01 -> sets requested registers to b'0x0B' and b'0x01' (vehicle speed and engine speed),
        # then instructs the ECU to start streaming data
        self.stop_stream = b'\x30'
        self.stop_ack = b'\xCF'

        self.parameters = [
            EcuParamDual("Engine Speed HR", b'\x00', b'\x01', "RPM", 12.5),
            EcuParamDual("Engine Speed LR", b'\x02', b'\x03', "RPM", 8),
            EcuParamDual("MAF Voltage", b'\x04', b'\x05', "mV", 5),
            EcuParamDual("MAF Voltage RH", b'\x06', b'\x07', "mV", 5),
            EcuParamSingle("Coolant Temp", b'\x08', "C", offset=-50),
            EcuParamSingle("O2 Voltage LH", b'\x09', "mV", 10),
            EcuParamSingle("O2 Voltage RH", b'\x0A', "mV", 10),
            EcuParamSingle("Vehicle Speed", b'\x0B', "km/h", 2),
            EcuParamSingle("Battery Voltage", b'\x0C', "V", 80),
            EcuParamSingle("TPS", b'\x0D', "%", 20),
            EcuParamSingle("Fuel Temp", b'\x0F', "C", offset=-50),
            EcuParamSingle("IAT", b'\x11', "C", offset=-50),
            EcuParamSingle("EGT", b'\x12', "mV", 20),
            EcuParamDual("Injector Time LH", b'\x14', b'\x15', "ms", 1/100),
            EcuParamSingle("Ignition Timing", b'\x16', "deg BTDC", -1, 110),
            EcuParamSingle("AAC Valve", b'\x17', "%", 1/2),
            EcuParamSingle("AF Alpha LH", b'\x1A', "%"),
            EcuParamSingle("AF Alpha RH", b'\x1B', "%"),
            EcuParamSingle("AF Alpha Selflearn LH", b'\x1C', "%"),
            EcuParamSingle("AF Alpha Selflearn RH", b'\x1D', "%"),
            EcuParamDual("Injector Time RH", b'\x22', b'\x23', "ms", 1/100),
            EcuParamSingle("Purge Valve Step", b'\x25', "steps"),
            EcuParamSingle("Tank Fuel Temp", b'\x26'),
            EcuParamSingle("FPCM Voltage", b'\x27', "V"),
            EcuParamSingle("WG Solenoid", b'\x28'),
            EcuParamSingle("Boost Voltage", b'\x29', "V"),
            EcuParamSingle("Engine Mount", b'\x2A'),
            EcuParamSingle("Position Counter", b'\x2E'),
            EcuParamSingle("Fuel Gauge Voltage", b'\x2F', "V"),
            EcuParamSingle("O2 Front B1 Voltage", b'\x30', "V"),
            EcuParamSingle("O2 Front B2 Voltage", b'\x31', "V"),
            EcuParamSingle("Ignition Switch", b'\x32'),
            EcuParamSingle("CAL LD Value", b'\x33'),
            EcuParamSingle("Fuel Schedule", b'\x34'),
            EcuParamSingle("O2 Rear B1 Voltage", b'\x35', "V"),
            EcuParamSingle("O2 Rear B2 Voltage", b'\x36', "V"),
            EcuParamSingle("Throttle Position ABS", b'\x37', "%"),
            EcuParamSingle("MAF Scaled", b'\x38', "g/s"),
            EcuParamSingle("Evap Pressure Voltage", b'\x39', "V"),
            EcuParamSingle("ABS Pressure Voltage A", b'\x3A', "V"),
            EcuParamSingle("ABS Pressure Voltage B", b'\x4A', "V"),
            EcuParamSingle("FPCM Pressure Voltage A", b'\x52', "V"),
            EcuParamSingle("FPCM Pressure Voltage B", b'\x53', "V"),
            EcuParamBit("A/C On", b'\x13', 4),
            EcuParamBit("Power Steering", b'\x13', 3),
            EcuParamBit("Park/Neutral", b'\x13', 2),
            EcuParamBit("Cranking", b'\x13', 1),
            EcuParamBit("CLSD/THL POS", b'\x13', 0),
            EcuParamBit("A/C Relay", b'\x1e', 7),
            EcuParamBit("Fuel Pump Relay", b'\x1e', 6),
            EcuParamBit("VTC Solenoid", b'\x1e', 5),
            EcuParamBit("Coolant Fan Hi", b'\x1e', 1),
            EcuParamBit("Coolant Fan Lo", b'\x1e', 0),
            EcuParamBit("P/Reg control valve", b'\x1f', 6),
            EcuParamBit("WG Solenoid", b'\x1f', 5),
            EcuParamBit("IACV FICD Solenoid", b'\x1f', 3),
            EcuParamBit("EGR Solenoid", b'\x1f', 0),
            EcuParamBit("LH Bank Lean", b'\x21', 7),
            EcuParamBit("RH Bank Lean", b'\x21', 6)]

        # perform a param sanity check -combination of registers + bit positions must be unique
        seen = set()
        for p in self.parameters:
            key = (p.get_registers(), p.bit if isinstance(p, EcuParamBit) else None)
            if key in seen:
                raise ValueError(f"ECU parameter Sanity Check failed: Duplicate parameter: {p.name}")
            seen.add(key)





    def get_parameters(self) -> list[EcuParam]:
        return self.parameters

    def get_enabled_parameters(self) -> list[EcuParam]:
        return [p for p in self.parameters if p.enabled]

    def count_enabled_parameters(self) -> int:
        return sum(1 for p in self.parameters if p.enabled)

    def get_param_from_register(self, register: bytes) -> EcuParam:
        for p in self.parameters:
            registers = p.get_registers()
            if len(registers) == 1 and registers == register:
                return p
            if p.get_registers() == register:
                return p
        raise ValueError(f"No parameter found for register {register}")
