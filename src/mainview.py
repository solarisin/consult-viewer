import sys
import logging

from PySide6.QtCore import QSize, Qt, Signal, Slot, QCoreApplication, QObject
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QTabWidget, QWidget, QLabel, \
    QCheckBox, QPlainTextEdit
from PySide6.QtGui import QFont

from consultmodel import ConsultInfo


#
# Signals need to be contained in a QObject or subclass in order to be correctly
# initialized.
#
class Signaller(QObject):
    signal = Signal(str, logging.LogRecord)


#
# Output to a Qt GUI is only supposed to happen on the main thread. So, this
# handler is designed to take a slot function which is set up to run in the main
# thread. In this example, the function takes a string argument which is a
# formatted log message, and the log record which generated it. The formatted
# string is just a convenience - you could format a string for output any way
# you like in the slot function itself.
#
# You specify the slot function to do whatever GUI updates you want. The handler
# doesn't know or care about specific UI elements.
#
class QtHandler(logging.Handler):
    def __init__(self, slot_func, *args, **kwargs):
        super(QtHandler, self).__init__(*args, **kwargs)
        self.signaller = Signaller()
        self.signaller.signal.connect(slot_func)

    def emit(self, record):
        s = self.format(record)
        self.signaller.signal.emit(s, record)


class TabTable(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel("Table Goes Here")
        layout.addWidget(label)
        self.setLayout(layout)


class TabOptions(QWidget):
    def __init__(self):
        super().__init__()

        def param_state_changed(ecu_param, state):
            print("State changed for param {} to {}".format(ecu_param.name, state))
            ecu_param.enable(state)

        i = 0
        params = ConsultInfo.get_params()
        layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        for param in params:
            check = QCheckBox(param.name)
            f = check.font()
            f.setPointSize(10)
            check.setFont(f)
            check.setContentsMargins(0, 0, 0, 0)
            check.stateChanged.connect(lambda state, p=param: param_state_changed(p, state == 2))
            if i % 2 == 0:
                layout1.addWidget(check)
            else:
                layout2.addWidget(check)
            i += 1
        layout1.setSpacing(1)
        layout2.setSpacing(1)

        layout = QHBoxLayout()
        layout.addLayout(layout1)
        layout.addLayout(layout2)
        self.setLayout(layout)


class LogView(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setFont(QFont("Courier New", 10))
        # self.setMaximumBlockCount(1000)
        self.handler = h = QtHandler(self.loghandler)
        fs = "%(asctime)s %(levelname)s [%(filename)s:%(lineno)s] %(message)s"
        formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s [%(filename)s:%(lineno)s] %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S")
        h.setFormatter(formatter)
        logging.getLogger().addHandler(h)

    @Slot(str, logging.LogRecord)
    def loghandler(self, status, record):
        self.append(status)

    def append(self, text):
        self.appendPlainText(text)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        QCoreApplication.processEvents()


class TabLog(QWidget):
    def __init__(self, logview):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(logview)
        self.setLayout(layout)


class MainView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)

        tabs = QTabWidget()
        tabs.addTab(TabTable(), "Table")
        tabs.addTab(TabOptions(), "Options")
        self.logview = LogView()
        tabs.addTab(TabLog(self.logview), "Log")

        layout.addWidget(tabs)

        self.setLayout(layout)
        # self.logview.append("Initiasslized.")
        logging.debug("Initfffialized.")
        # self.logview.append("Initializessd 2.")
        logging.debug("Initialfffized 2.")


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        # Construct the main view and set it as the central widget
        self._mainview = MainView()
        self.setCentralWidget(self._mainview)


# Entrypoint
if __name__ == "__main__":
    app = QApplication(sys.argv)

    logging.basicConfig(
        format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG)

    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.excepthook = handle_exception

    window = MainWindow()
    window.show()

    app.exec()
