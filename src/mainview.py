import sys
import logging
from abc import ABCMeta, ABC, abstractmethod
from typing import Callable

from PySide6.QtCore import Signal, Slot, QCoreApplication, QObject, QSize, QSignalBlocker
from PySide6.QtWidgets import QSizePolicy, QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, \
    QCheckBox, QPlainTextEdit, QMessageBox, QTableView, QAbstractItemView, QGroupBox, QInputDialog, QComboBox, \
    QWidgetAction
from PySide6.QtGui import QFont, QAction

import PySide6QtAds as QtAds

from consultmodel import ConsultInfo, ConsultParameterTableModel


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


# class QABCMeta(ABCMeta, type(QWidget)):
#     pass
#
#
# class DockableView(ABC, metaclass=QABCMeta):
#     @abstractmethod
#     def dock_size(self) -> QSize:
#         pass


class TableView(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        table = QTableView(self)
        table.setContentsMargins(0, 0, 0, 0)

        # Create and populate the tableWidget
        # table.setItemDelegate(StarDelegate())
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setModel(ConsultParameterTableModel())
        layout.addWidget(table)
        self.setLayout(layout)


class OptionsView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        param_gb = QGroupBox("ECU Parameters", self)
        param_layout = QVBoxLayout(param_gb)
        for param in ConsultInfo.get_params():
            param_layout.addWidget(self.create_param_checkbox(param))
        layout.addWidget(param_gb)
        self.setLayout(layout)

    @staticmethod
    def create_param_checkbox(param):
        def param_state_changed(ecu_param, state):
            logging.debug("State changed for param {} to {}".format(ecu_param.name, state))
            ecu_param.enable(state)
        check = QCheckBox(param.name)
        f = check.font()
        f.setPointSize(10)
        check.setFont(f)
        check.setContentsMargins(0, 0, 0, 0)
        check.stateChanged.connect(lambda state, p=param: param_state_changed(p, state == 2))
        return check


class LogView(QPlainTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
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


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.FocusHighlighting, True)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.DockAreaHasTabsMenuButton, False)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.OpaqueSplitterResize, True)
        QtAds.CDockManager.setAutoHideConfigFlags(QtAds.CDockManager.DefaultAutoHideConfig)
        # QtAds.CDockManager.setAutoHideConfigFlag(QtAds.CDockManager.AutoHideShowOnMouseOver, True)
        QtAds.CDockManager.setAutoHideConfigFlag(QtAds.CDockManager.AutoHideCloseButtonCollapsesDock, True)
        QtAds.CDockManager.setAutoHideConfigFlag(QtAds.CDockManager.AutoHideHasMinimizeButton, False)
        self._dock_mgr = QtAds.CDockManager(self)

        self._save_perspective_act = None
        self._perspective_list_act = None
        self._perspective_combo = None
        self._quit_act = None
        self._about_act = None
        self._about_qt_act = None
        self.create_actions()

        self._file_menu = None
        self._view_menu = None
        self._help_menu = None
        self.create_menus()

        self._perspective_tool_bar = None
        self.create_tool_bars()

        self.create_status_bar()

        self._table_view = None
        self._log_view = None
        self._options_view = None
        self.create_dock_windows()

        self.setWindowTitle("Consult Viewer")

        logging.debug("Main window initialized.")

    def about(self):
        QMessageBox.about(self, "About Dock Widgets",
                          "The <b>Dock Widgets</b> example demonstrates how to use "
                          "Qt's dock widgets. You can enter your own text, click a "
                          "customer to add a customer name and address, and click "
                          "standard paragraphs to add them.")

    def create_actions(self):
        # icon = QIcon.fromTheme('document-new', QIcon(':/res/new.png'))
        # self._new_letter_act = QAction(icon, "&New Letter",
        #                                self, shortcut=QKeySequence.New,
        #                                statusTip="Create a new form letter",
        #                                triggered=self.new_letter)
        #
        # icon = QIcon.fromTheme('document-save', QIcon(':/res/save.png'))
        # self._save_act = QAction(icon, "&Save...", self,
        #                          shortcut=QKeySequence.Save,
        #                          statusTip="Save the current form letter", triggered=self.save)
        #
        # icon = QIcon.fromTheme('document-print', QIcon(':/res/print.png'))
        # self._print_act = QAction(icon, "&Print...", self,
        #                           shortcut=QKeySequence.Print,
        #                           statusTip="Print the current form letter",
        #                           triggered=self.print_)
        #
        # icon = QIcon.fromTheme('edit-undo', QIcon(':/res/undo.png'))
        # self._undo_act = QAction(icon, "&Undo", self,
        #                          shortcut=QKeySequence.Undo,
        #                          statusTip="Undo the last editing action", triggered=self.undo)

        self._quit_act = QAction("&Quit",
                                 parent=self,
                                 shortcut="Ctrl+Q",
                                 statusTip="Quit the application",
                                 triggered=self.close)

        self._about_act = QAction("&About",
                                  parent=self,
                                  statusTip="Show the application's About box",
                                  triggered=self.about)

        self._about_qt_act = QAction("About &Qt", parent=self,
                                     statusTip="Show the Qt library's About box",
                                     triggered=QApplication.instance().aboutQt)

        self._save_perspective_act = QAction("Create Perspective", parent=self,
                                     statusTip="Save the current perspective",
                                     triggered=self.save_perspective)

        self._perspective_list_act = QWidgetAction(self)
        self._perspective_combo = QComboBox(self)
        self._perspective_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self._perspective_combo.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        self._perspective_combo.currentTextChanged.connect(self._dock_mgr.openPerspective)
        self._perspective_list_act.setDefaultWidget(self._perspective_combo)

    def create_menus(self):
        self._file_menu = self.menuBar().addMenu("&File")
        # self._file_menu.addAction(self._new_letter_act)
        # self._file_menu.addAction(self._save_act)
        # self._file_menu.addAction(self._print_act)
        # self._file_menu.addSeparator()
        self._file_menu.addAction(self._quit_act)

        # self._edit_menu = self.menuBar().addMenu("&Edit")
        # self._edit_menu.addAction(self._undo_act)

        self._view_menu = self.menuBar().addMenu("&View")

        self.menuBar().addSeparator()

        self._help_menu = self.menuBar().addMenu("&Help")
        self._help_menu.addAction(self._about_act)
        self._help_menu.addAction(self._about_qt_act)

    def create_tool_bars(self):
        pass
        self._perspective_tool_bar = self.addToolBar("Perspective")
        self._perspective_tool_bar.addAction(self._perspective_list_act)
        self._perspective_tool_bar.addAction(self._save_perspective_act)

    #     self._file_tool_bar.addAction(self._new_letter_act)
    #     self._file_tool_bar.addAction(self._save_act)
    #     self._file_tool_bar.addAction(self._print_act)
    #
    #     self._edit_tool_bar = self.addToolBar("Edit")
    #     self._edit_tool_bar.addAction(self._undo_act)

    def create_status_bar(self):
        self.statusBar().showMessage("Ready")

    def save_perspective(self):
        name, entered = QInputDialog.getText(self, "Save Perspective", "Enter unique name:")
        if not entered or len(name) == 0:
            return

        self._dock_mgr.addPerspective(name)
        QSignalBlocker(self._perspective_combo)
        self._perspective_combo.clear()
        self._perspective_combo.addItems(self._dock_mgr.perspectiveNames())
        self._perspective_combo.setCurrentText(name)

    def create_dock_windows(self):
        def create_and_dock_view(title, area, instantiate: Callable[[QtAds.CDockWidget], QWidget]):
            dock = QtAds.CDockWidget(title, self)
            # dock.setAllowedAreasQt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
            dockable = instantiate(dock)
            dock.setWidget(dockable)
            dock.setMinimumSizeHintMode(QtAds.CDockWidget.MinimumSizeHintFromDockWidget)
            dock.resize(800, 800)
            dock.setMinimumSize(800, 800)
            if isinstance(area, QtAds.DockWidgetArea):
                self._dock_mgr.addDockWidget(area, dock)
            else:
                self._dock_mgr.addAutoHideDockWidget(area, dock)
            self._view_menu.addAction(dock.toggleViewAction())

        # set the table view as the central widget (the main view)
        table_dock = QtAds.CDockWidget("Table", self)
        table_dock.setWidget(TableView(table_dock))
        self._dock_mgr.setCentralWidget(table_dock)

        create_and_dock_view("Options", QtAds.SideBarRight, lambda d: OptionsView(d))
        create_and_dock_view("Log", QtAds.BottomDockWidgetArea, lambda d: LogView(d))


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

    window.resize(1600, 900)
    window.show()

    app.exec()
