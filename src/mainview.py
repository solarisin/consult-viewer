import sys
import logging
from abc import ABCMeta, ABC, abstractmethod
from typing import Callable

from PySide6.QtCore import Signal, Slot, QCoreApplication, QObject, QSettings
from PySide6.QtWidgets import QSizePolicy, QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, \
    QCheckBox, QPlainTextEdit, QMessageBox, QTableView, QAbstractItemView, QGroupBox, QInputDialog
from PySide6.QtGui import QFont, QAction

import PySide6QtAds as QtAds

from consultmodel import ConsultInfo, ConsultParameterTableModel


def resize_font(font: QFont, point_size: int):
    f = QFont(font)
    f.setPointSize(point_size)
    return f


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


class QABCMeta(ABCMeta, type(QWidget)):
    pass


class DockableView(ABC, metaclass=QABCMeta):
    @abstractmethod
    def initial_expanded_size(self) -> int:
        pass


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


class OptionsView(QWidget, DockableView):
    def __init__(self, parent):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        param_gb = QGroupBox("ECU Parameters", self)
        param_layout = QVBoxLayout(param_gb)
        for param in ConsultInfo.get_params():
            param_layout.addWidget(self.create_param_checkbox(param))
        layout.addWidget(param_gb)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    @staticmethod
    def create_param_checkbox(param):
        def param_state_changed(ecu_param, state):
            logging.debug("State changed for param {} to {}".format(ecu_param.name, state))
            ecu_param.enable(state)
        check = QCheckBox(param.name)
        check.setFont(resize_font(check.font(), 10))
        check.setContentsMargins(0, 0, 0, 0)
        check.stateChanged.connect(lambda state, p=param: param_state_changed(p, state == 2))
        return check

    def initial_expanded_size(self) -> int:
        return self.layout().layout().sizeHint().width() + 20


class LogView(QPlainTextEdit, DockableView):
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

    def initial_expanded_size(self) -> int:
        return self.layout().layout().sizeHint().width()


# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # init vars
        self._store_perspective_act = None
        self._delete_perspective_act = None
        self._quit_act = None
        self._about_act = None
        self._about_qt_act = None

        self._file_menu = None
        self._view_menu = None
        self._windows_menu = None
        self._help_menu = None

        self._table_view = None
        self._log_view = None
        self._options_view = None

        self._perspective_settings_file = QSettings("cv_settings.cfg", QSettings.Format.IniFormat)

        # setup dock manager
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.FocusHighlighting, True)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.DockAreaHasTabsMenuButton, False)
        QtAds.CDockManager.setConfigFlag(QtAds.CDockManager.OpaqueSplitterResize, True)
        QtAds.CDockManager.setAutoHideConfigFlags(QtAds.CDockManager.DefaultAutoHideConfig)
        # QtAds.CDockManager.setAutoHideConfigFlag(QtAds.CDockManager.AutoHideShowOnMouseOver, True)
        QtAds.CDockManager.setAutoHideConfigFlag(QtAds.CDockManager.AutoHideCloseButtonCollapsesDock, True)
        QtAds.CDockManager.setAutoHideConfigFlag(QtAds.CDockManager.AutoHideHasMinimizeButton, False)
        self._dock_mgr = QtAds.CDockManager(self)

        # load perspectives
        self._dock_mgr.loadPerspectives(self._perspective_settings_file)
        self._current_perspective = ""

        # setup main window
        self.create_actions()
        self.create_menus()
        self.create_status_bar()
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

        self._store_perspective_act = QAction("Save",
                                              parent=self,
                                              statusTip="Save the current perspective",
                                              triggered=self.store_perspective)

        self._delete_perspective_act = QAction("Delete",
                                               parent=self,
                                               statusTip="Remove a perspective",
                                               triggered=self.delete_perspective)

    def create_menus(self):
        self._file_menu = self.menuBar().addMenu("&File")
        self._file_menu.addAction(self._quit_act)
        self._view_menu = self.menuBar().addMenu("&View")
        perspective_menu = self._view_menu.addMenu("Perspectives")

        def refresh_perspective_actions():
            def handle_perspective_selected(name):
                self._current_perspective = name
                logging.info(f"Loading perspective '{name}'")
                self._dock_mgr.openPerspective(name)
            perspective_menu.clear()
            for perspective_name in self._dock_mgr.perspectiveNames():
                action = QAction(perspective_name, self, statusTip=f"Load the '{perspective_name}' perspective")
                action.triggered.connect(lambda checked, n=perspective_name: handle_perspective_selected(n))
                perspective_menu.addAction(action)
            perspective_menu.addSeparator()
            perspective_menu.addAction(self._store_perspective_act)
            perspective_menu.addAction(self._delete_perspective_act)

        perspective_menu.aboutToShow.connect(refresh_perspective_actions)
        self._view_menu.addSeparator()
        self._windows_menu = self._view_menu.addMenu("Windows")

        self.menuBar().addSeparator()

        self._help_menu = self.menuBar().addMenu("&Help")
        self._help_menu.addAction(self._about_act)
        self._help_menu.addAction(self._about_qt_act)

    def create_status_bar(self):
        self.statusBar().showMessage("Ready")

    def store_perspective(self):
        name, entered = QInputDialog.getText(self, "Save Perspective", "Enter unique name:")
        if not entered or len(name) == 0:
            return

        self._dock_mgr.addPerspective(name)
        logging.info(f"Added perspective '{name}'")
        self._dock_mgr.savePerspectives(self._perspective_settings_file)

    def delete_perspective(self):
        perspective_names = self._dock_mgr.perspectiveNames()
        if len(perspective_names) <= 1:
            return

        try:
            current = perspective_names.index(self._current_perspective)
        except ValueError:
            current = 0

        selected, ok = QInputDialog.getItem(self, "Delete Perspective", "Select perspective to delete:",
                                            self._dock_mgr.perspectiveNames(),
                                            current=current,
                                            editable=False)
        if ok:
            self._dock_mgr.removePerspective(selected)
            logging.info(f"Removed perspective '{selected}'")
            self._dock_mgr.savePerspectives(self._perspective_settings_file)

    def create_dock_windows(self):
        def create_and_dock_view(title, area, instantiate: Callable[[QtAds.CDockWidget], DockableView]):
            dock = QtAds.CDockWidget(title, self)
            dockable = instantiate(dock)
            dock.setWidget(dockable)
            # dock.setMinimumSizeHintMode(QtAds.CDockWidget.MinimumSizeHintFromDockWidget)
            dock.setMinimumSizeHintMode(QtAds.CDockWidget.MinimumSizeHintFromContent)
            if isinstance(area, QtAds.DockWidgetArea):
                self._dock_mgr.addDockWidget(area, dock)
            else:
                container = self._dock_mgr.addAutoHideDockWidget(area, dock)
                container.setSize(dockable.initial_expanded_size())
                container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

            self._windows_menu.addAction(dock.toggleViewAction())

        # set the table view as the central widget (the main view)
        table_dock = QtAds.CDockWidget("Table", self)
        table_dock.setWidget(TableView(table_dock))
        table_dock.setMinimumSizeHintMode(QtAds.CDockWidget.MinimumSizeHintFromContent)
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
