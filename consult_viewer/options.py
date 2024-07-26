import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QCheckBox, QHBoxLayout, QVBoxLayout, QGroupBox, QSizePolicy
import consult_interface as consult
from dockutils import DockableView
from utility import resize_font


class OptionsView(QWidget, DockableView):
    parameterSelectionChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        param_selection = self.setup_parameter_selection()
        layout.addWidget(param_selection)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def setup_parameter_selection(self):
        def create_param_checkbox(param):
            def param_state_changed(ecu_param, state):
                logging.debug("State changed for param {} to {}".format(ecu_param.name, state))
                ecu_param.enable(state)
                self.parameterSelectionChanged.emit()

            check = QCheckBox(param.name)
            check.setFont(resize_font(check.font(), 10))
            check.setContentsMargins(0, 0, 0, 0)
            check.stateChanged.connect(lambda state, p=param: param_state_changed(p, state == 2))
            return check

        param_gb = QGroupBox("ECU Parameters", self)
        param_layout = QVBoxLayout(param_gb)
        for param_def in consult.Definition.get_parameters():
            param_layout.addWidget(create_param_checkbox(param_def))
        return param_gb

    def initial_expanded_size(self) -> int:
        return self.layout().layout().sizeHint().width() + 20
