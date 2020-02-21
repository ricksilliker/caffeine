import logging
import math
import platform

from maya.api import OpenMaya
from maya.api import OpenMayaUI as omui
from maya import OpenMayaUI, cmds
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore

import logs


LOG = logs.getLogger(__name__)
__all__ = ['main', 'mayaMainWindow']


def main():
    pass


def mayaMainWindow():
    """Get Maya's main window as a QWidget."""
    OpenMayaUI.MQtUtil.mainWindow()
    ptr = OpenMayaUI.MQtUtil.mainWindow()

    return wrapInstance(long(ptr), QtWidgets.QWidget)


class AbstractWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AbstractWidget, self).__init__(parent=parent)

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

    @classmethod
    def run(cls):
        """Creates an instance of the QWidget and shows it in Maya's main view."""
        app = mayaMainWindow()
        
        widget = cls(parent=app)

        widget.setWidowFlags(widget.windowFlags() | QtCore.Qt.Window)

        if platform.system() == 'Darwin':
            # MacOS is special, and the QtCore.Qt.Window flag does not sort the windows properly,
            # so instead QtCore.Qt.Tool is used.
            widget.setWindowFlags(widget.windowFlags() | QtCore.Qt.Tool)
        # Center the widget with Maya's main window.
        widget.move(app.frameGeometry().center() - QtCore.QRect(QtCore.QPoint(), widget.sizeHint()).center())
        
        widget.show()

        return widget


