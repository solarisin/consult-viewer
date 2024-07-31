from abc import ABC, abstractmethod
from typing import Callable

import serial
import threading
from timer import timer


# base class for communication to the nissan consult UART interface over a usb serial connection
class ConsultSerial(ABC):
    def __init__(self, port: str):
        self._port = port
        self._baud = 9600

    @abstractmethod
    def _open(self):
        pass

    @abstractmethod
    def _close(self):
        pass

    @abstractmethod
    def _write(self, data):
        pass

    @abstractmethod
    def _read(self):
        pass


# Thread class for reading ECU parameter frames from the serial port
class ReadParamFramesThread(threading.Thread):
    def __init__(self, port: serial.Serial, frame_bytes: int, process_frame: Callable[[bytes], None]):
        threading.Thread.__init__(self)
        self._frame_size = frame_bytes
        self._port = port
        self._running = False
        self.process_frame = process_frame

    def run(self):
        @timer
        def process_read(frame):
            return self.process_frame(frame)

        port_opened = False
        if not self._port.open():
            self._port.open()
            port_opened = True

        self._running = True
        while self._running:
            if self._port.in_waiting > self._frame_size:
                read_bytes = self._port.read(self._frame_size)
                if read_bytes:
                    process_read(read_bytes)

        if port_opened:
            self._port.close()

    def stop(self):
        self._running = False


# Implementation of the ConsultSerial class for the actual serial communication
class ConsultSerialImpl(ConsultSerial):
    def __init__(self, port: str):
        super().__init__(port)
        self._serial = serial.Serial(self._port, self._baud, timeout=None, xonxoff=False, rtscts=False, dsrdtr=False)

    def _open(self):
        pass

    def _close(self):
        self._serial.close()

    def _write(self, data):
        self._serial.write(data)

    def _read(self):
        return self._serial.read()


class ConsultSerialMock(ConsultSerial):
    def __init__(self):
        super().__init__("mock")

    def open(self):
        pass

    def close(self):
        pass

    def write(self, data):
        pass

    def read(self):
        pass


def create(port: str, mock=False) -> ConsultSerial:
    if mock:
        return ConsultSerialMock()
    else:
        return ConsultSerialImpl(port)
