from PySide6.QtGui import QFont


def resize_font(font: QFont, point_size: int):
    f = QFont(font)
    f.setPointSize(point_size)
    return f
