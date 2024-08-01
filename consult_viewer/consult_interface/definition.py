from .params import EcuParam, EcuParamSingle, EcuParamDual, EcuParamBit
from enum import IntEnum


class ParamID(IntEnum):
    ENGINE_SPEED_HR = 0
    ENGINE_SPEED_LR = 1
    MAF_VOLTAGE = 2
    MAF_VOLTAGE_RH = 3
    COOLANT_TEMP = 4
    O2_VOLTAGE_LH = 5
    O2_VOLTAGE_RH = 6
    VEHICLE_SPEED = 7
    BATTERY_VOLTAGE = 8
    TPS = 9
    FUEL_TEMP = 10
    IAT = 11
    EGT = 12
    INJECTOR_TIME_LH = 13
    IGNITION_TIMING = 14
    AAC_VALVE = 15
    AF_ALPHA_LH = 16
    AF_ALPHA_RH = 17
    AF_ALPHA_SELFLEARN_LH = 18
    AF_ALPHA_SELFLEARN_RH = 19
    INJECTOR_TIME_RH = 20
    PURGE_VALVE_STEP = 21
    TANK_FUEL_TEMP = 22
    FPCM_VOLTAGE = 23
    WG_SOLENOID_POS = 24
    BOOST_VOLTAGE = 25
    ENGINE_MOUNT = 26
    POSITION_COUNTER = 27
    FUEL_GAUGE_VOLTAGE = 28
    O2_FRONT_B1_VOLTAGE = 29
    O2_FRONT_B2_VOLTAGE = 30
    IGNITION_SWITCH = 31
    CAL_LD_VALUE = 32
    FUEL_SCHEDULE = 33
    O2_REAR_B1_VOLTAGE = 34
    O2_REAR_B2_VOLTAGE = 35
    THROTTLE_POSITION_ABS = 36
    MAF_SCALED = 37
    EVAP_PRESSURE_VOLTAGE = 38
    ABS_PRESSURE_VOLTAGE_A = 39
    ABS_PRESSURE_VOLTAGE_B = 40
    FPCM_PRESSURE_VOLTAGE_A = 41
    FPCM_PRESSURE_VOLTAGE_B = 42
    AC_ON = 43
    POWER_STEERING = 44
    PARK_NEUTRAL = 45
    CRANKING = 46
    CLSD_THL_POS = 47
    AC_RELAY = 48
    FUEL_PUMP_RELAY = 49
    VTC_SOLENOID = 50
    COOLANT_FAN_HI = 51
    COOLANT_FAN_LO = 52
    P_REG_CONTROL_VALVE = 53
    WG_SOLENOID_STATE = 54
    IACV_FICD_SOLENOID = 55
    EGR_SOLENOID = 56
    LH_BANK_LEAN = 57
    RH_BANK_LEAN = 58


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

        self.parameters = dict()
        self.parameters[ParamID.ENGINE_SPEED_HR] = EcuParamDual("Engine Speed HR", b'\x00', b'\x01', "RPM", 12.5)
        self.parameters[ParamID.ENGINE_SPEED_LR] = EcuParamDual("Engine Speed LR", b'\x02', b'\x03', "RPM", 8)
        self.parameters[ParamID.MAF_VOLTAGE] = EcuParamDual("MAF Voltage", b'\x04', b'\x05', "mV", 5)
        self.parameters[ParamID.MAF_VOLTAGE_RH] = EcuParamDual("MAF Voltage RH", b'\x06', b'\x07', "mV", 5)
        self.parameters[ParamID.COOLANT_TEMP] = EcuParamSingle("Coolant Temp", b'\x08', "C", offset=-50)
        self.parameters[ParamID.O2_VOLTAGE_LH] = EcuParamSingle("O2 Voltage LH", b'\x09', "mV", 10)
        self.parameters[ParamID.O2_VOLTAGE_RH] = EcuParamSingle("O2 Voltage RH", b'\x0A', "mV", 10)
        self.parameters[ParamID.VEHICLE_SPEED] = EcuParamSingle("Vehicle Speed", b'\x0B', "km/h", 2)
        self.parameters[ParamID.BATTERY_VOLTAGE] = EcuParamSingle("Battery Voltage", b'\x0C', "V", 80)
        self.parameters[ParamID.TPS] = EcuParamSingle("TPS", b'\x0D', "%", 20)
        self.parameters[ParamID.FUEL_TEMP] = EcuParamSingle("Fuel Temp", b'\x0F', "C", offset=-50)
        self.parameters[ParamID.IAT] = EcuParamSingle("IAT", b'\x11', "C", offset=-50)
        self.parameters[ParamID.EGT] = EcuParamSingle("EGT", b'\x12', "mV", 20)
        self.parameters[ParamID.INJECTOR_TIME_LH] = EcuParamDual("Injector Time LH", b'\x14', b'\x15', "ms", 1/100)
        self.parameters[ParamID.IGNITION_TIMING] = EcuParamSingle("Ignition Timing", b'\x16', "deg BTDC", -1, 110)
        self.parameters[ParamID.AAC_VALVE] = EcuParamSingle("AAC Valve", b'\x17', "%", 1/2)
        self.parameters[ParamID.AF_ALPHA_LH] = EcuParamSingle("AF Alpha LH", b'\x1A', "%")
        self.parameters[ParamID.AF_ALPHA_RH] = EcuParamSingle("AF Alpha RH", b'\x1B', "%")
        self.parameters[ParamID.AF_ALPHA_SELFLEARN_LH] = EcuParamSingle("AF Alpha Selflearn LH", b'\x1C', "%")
        self.parameters[ParamID.AF_ALPHA_SELFLEARN_RH] = EcuParamSingle("AF Alpha Selflearn RH", b'\x1D', "%")
        self.parameters[ParamID.INJECTOR_TIME_RH] = EcuParamDual("Injector Time RH", b'\x22', b'\x23', "ms", 1/100)
        self.parameters[ParamID.PURGE_VALVE_STEP] = EcuParamSingle("Purge Valve Step", b'\x25', "steps")
        self.parameters[ParamID.TANK_FUEL_TEMP] = EcuParamSingle("Tank Fuel Temp", b'\x26')
        self.parameters[ParamID.FPCM_VOLTAGE] = EcuParamSingle("FPCM Voltage", b'\x27', "V")
        self.parameters[ParamID.WG_SOLENOID_POS] = EcuParamSingle("WG Solenoid Pos", b'\x28')
        self.parameters[ParamID.BOOST_VOLTAGE] = EcuParamSingle("Boost Voltage", b'\x29', "V")
        self.parameters[ParamID.ENGINE_MOUNT] = EcuParamSingle("Engine Mount", b'\x2A')
        self.parameters[ParamID.POSITION_COUNTER] = EcuParamSingle("Position Counter", b'\x2E')
        self.parameters[ParamID.FUEL_GAUGE_VOLTAGE] = EcuParamSingle("Fuel Gauge Voltage", b'\x2F', "V")
        self.parameters[ParamID.O2_FRONT_B1_VOLTAGE] = EcuParamSingle("O2 Front B1 Voltage", b'\x30', "V")
        self.parameters[ParamID.O2_FRONT_B2_VOLTAGE] = EcuParamSingle("O2 Front B2 Voltage", b'\x31', "V")
        self.parameters[ParamID.IGNITION_SWITCH] = EcuParamSingle("Ignition Switch", b'\x32')
        self.parameters[ParamID.CAL_LD_VALUE] = EcuParamSingle("CAL LD Value", b'\x33')
        self.parameters[ParamID.FUEL_SCHEDULE] = EcuParamSingle("Fuel Schedule", b'\x34')
        self.parameters[ParamID.O2_REAR_B1_VOLTAGE] = EcuParamSingle("O2 Rear B1 Voltage", b'\x35', "V")
        self.parameters[ParamID.O2_REAR_B2_VOLTAGE] = EcuParamSingle("O2 Rear B2 Voltage", b'\x36', "V")
        self.parameters[ParamID.THROTTLE_POSITION_ABS] = EcuParamSingle("Throttle Position ABS", b'\x37', "%")
        self.parameters[ParamID.MAF_SCALED] = EcuParamSingle("MAF Scaled", b'\x38', "g/s")
        self.parameters[ParamID.EVAP_PRESSURE_VOLTAGE] = EcuParamSingle("Evap Pressure Voltage", b'\x39', "V")
        self.parameters[ParamID.ABS_PRESSURE_VOLTAGE_A] = EcuParamSingle("ABS Pressure Voltage A", b'\x3A', "V")
        self.parameters[ParamID.ABS_PRESSURE_VOLTAGE_B] = EcuParamSingle("ABS Pressure Voltage B", b'\x4A', "V")
        self.parameters[ParamID.FPCM_PRESSURE_VOLTAGE_A] = EcuParamSingle("FPCM Pressure Voltage A", b'\x52', "V")
        self.parameters[ParamID.FPCM_PRESSURE_VOLTAGE_B] = EcuParamSingle("FPCM Pressure Voltage B", b'\x53', "V")
        self.parameters[ParamID.AC_ON] = EcuParamBit("A/C On", b'\x13', 4)
        self.parameters[ParamID.POWER_STEERING] = EcuParamBit("Power Steering", b'\x13', 3)
        self.parameters[ParamID.PARK_NEUTRAL] = EcuParamBit("Park/Neutral", b'\x13', 2)
        self.parameters[ParamID.CRANKING] = EcuParamBit("Cranking", b'\x13', 1)
        self.parameters[ParamID.CLSD_THL_POS] = EcuParamBit("CLSD/THL POS", b'\x13', 0)
        self.parameters[ParamID.AC_RELAY] = EcuParamBit("A/C Relay", b'\x1e', 7)
        self.parameters[ParamID.FUEL_PUMP_RELAY] = EcuParamBit("Fuel Pump Relay", b'\x1e', 6)
        self.parameters[ParamID.VTC_SOLENOID] = EcuParamBit("VTC Solenoid", b'\x1e', 5)
        self.parameters[ParamID.COOLANT_FAN_HI] = EcuParamBit("Coolant Fan Hi", b'\x1e', 1)
        self.parameters[ParamID.COOLANT_FAN_LO] = EcuParamBit("Coolant Fan Lo", b'\x1e', 0)
        self.parameters[ParamID.P_REG_CONTROL_VALVE] = EcuParamBit("P/Reg control valve", b'\x1f', 6)
        self.parameters[ParamID.WG_SOLENOID_STATE] = EcuParamBit("WG Solenoid State", b'\x1f', 5)
        self.parameters[ParamID.IACV_FICD_SOLENOID] = EcuParamBit("IACV FICD Solenoid", b'\x1f', 3)
        self.parameters[ParamID.EGR_SOLENOID] = EcuParamBit("EGR Solenoid", b'\x1f', 0)
        self.parameters[ParamID.LH_BANK_LEAN] = EcuParamBit("LH Bank Lean", b'\x21', 7)
        self.parameters[ParamID.RH_BANK_LEAN] = EcuParamBit("RH Bank Lean", b'\x21', 6)

        self._param_array = [EcuParamDual("Engine Speed HR", b'\x00', b'\x01', "RPM", 12.5),
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
            EcuParamSingle("WG Solenoid Pos", b'\x28'),
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
            EcuParamBit("WG Solenoid State", b'\x1f', 5),
            EcuParamBit("IACV FICD Solenoid", b'\x1f', 3),
            EcuParamBit("EGR Solenoid", b'\x1f', 0),
            EcuParamBit("LH Bank Lean", b'\x21', 7),
            EcuParamBit("RH Bank Lean", b'\x21', 6)]

        # perform a param sanity check -combination of registers + bit positions must be unique
        seen = set()
        for id, p in self.parameters.items():
            key = (p.get_registers(), p.bit if isinstance(p, EcuParamBit) else None)
            if key in seen:
                raise ValueError(f"ECU parameter Sanity Check failed: Duplicate parameter: {p.name}")
            seen.add(key)

        if len(self.parameters) != len(self._param_array):
            raise ValueError("ECU parameter Sanity Check failed: parameters list length mismatch")
        for i in range(0, len(self._param_array)):
            lhs = self.parameters[i]
            rhs = self._param_array[i]
            if lhs.name != rhs.name:
                raise ValueError(f"ECU parameter Sanity Check failed: name mismatch at index {i}")
            if lhs.get_registers() != rhs.get_registers():
                raise ValueError(f"ECU parameter Sanity Check failed: register mismatch at index {i}")
            if lhs.unit_label != rhs.unit_label:
                raise ValueError(f"ECU parameter Sanity Check failed: unit_label mismatch at index {i}")
            if lhs.scale != rhs.scale:
                raise ValueError(f"ECU parameter Sanity Check failed: scale mismatch at index {i}")
            if lhs.offset != rhs.offset:
                raise ValueError(f"ECU parameter Sanity Check failed: offset mismatch at index {i}")
            if lhs.enabled != rhs.enabled:
                raise ValueError(f"ECU parameter Sanity Check failed: enabled mismatch at index {i}")
            if lhs.__class__ != rhs.__class__:
                raise ValueError(f"ECU parameter Sanity Check failed: class mismatch at index {i}")
            if lhs.__class__ == EcuParamDual:
                if lhs.register_msb != rhs.register_msb:
                    raise ValueError(f"ECU parameter Sanity Check failed: register_msb mismatch at index {i}")
                if lhs.register_lsb != rhs.register_lsb:
                    raise ValueError(f"ECU parameter Sanity Check failed: register_lsb mismatch at index {i}")
            if lhs.__class__ == EcuParamSingle:
                if lhs.register != rhs.register:
                    raise ValueError(f"ECU parameter Sanity Check failed: register mismatch at index {i}")
            if lhs.__class__ == EcuParamBit:
                if lhs.bit != rhs.bit:
                    raise ValueError(f"ECU parameter Sanity Check failed: bit mismatch at index {i}")







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
