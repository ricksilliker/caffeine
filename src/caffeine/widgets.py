import logging
import math
import platform

from maya.api import OpenMaya
from maya.api import OpenMayaUI as omui
from maya import OpenMayaUI, cmds
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore, QtGui

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

        widget.setWindowFlags(widget.windowFlags() | QtCore.Qt.Window)

        if platform.system() == 'Darwin':
            # MacOS is special, and the QtCore.Qt.Window flag does not sort the windows properly,
            # so QtCore.Qt.Tool is added.
            widget.setWindowFlags(widget.windowFlags() | QtCore.Qt.Tool)
        
        # Center the widget with Maya's main window.
        widget.move(app.frameGeometry().center() - QtCore.QRect(QtCore.QPoint(), widget.sizeHint()).center())
        
        widget.show()

        return widget


def getDataWidget(dataType, configuration):
    field = None
    
    if dataType == 'string':
        field = QtWidgets.QLineEdit()
    elif dataType == 'float':
        field = QtWidgets.QDoubleSpinBox()
        field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
    elif dataType == 'list':
        field = DataListWidget(configuration)


    return field


def createFieldWithLabel(field, labelText):
    widget = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout(widget)
    layout.setAlignment(QtCore.AlignLeft)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(5)
    
    labelWidget = QtWidgets.QLabel(labelText)
    layout.addWidget(labelWidget)
    
    layout.addWidget(field)

    return widget


class DataStringWidget(AbstractWidget):
    def __init__(self, config, parent=None):
        super(DataStringWidget, self).__init__(parent=parent)

        if 'enum' in config:
            self.field = QtWidgets.QComboBox()
            self.field.addItems(config['enum'])
            
            if 'default' in config:
                for i in range(self.field.count()):
                    if self.field.itemText(i) == config['default']:
                        self.field.setCurrentIndex(i)
                        break
        else:
            self.field = QtWidgets.QLineEdit()

            if 'pattern' in config:
                regex = QtCore.QRegExp(config['pattern'])
                regexValidator = QtGui.QRegExpValidator(regex)
                self.field.setValidator(regexValidator)

            if 'default' in config:
                self.field.setText(config['default'])

        if 'description' in config:
            self.setToolTip(config['description'])

        self.layout().addWidget(self.field)


class DataFloatWidget(AbstractWidget):
    def __init__(self, config, parent=None):
        super(DataFloatWidget, self).__init__(parent=parent)

        self.field = QtWidgets.QDoubleSpinBox()
        self.field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        
        if 'description' in config:
            self.field.setToolTip(config['description'])

        if 'minimum' in config:
            self.field.setMinimum(config['minimum'])

        if 'maximum' in config:
            self.field.setMaximum(config['maximum'])

        self.layout().addWidget(self.field)


class DataListWidget(AbstractWidget):
    def __init__(self, config, parent=None):
        super(DataListWidget, self).__init__(parent=parent)

        self.layout().setDirection(QtWidgets.QBoxLayout.LeftToRight)

        self.fields = []

        if 'format' in config:
            if config['format'] == 'vec3':
                for x, axis in enumerate(['X', 'Y', 'Z']):
                    field = getDataWidget(config['items']['type'], config['items'])
                    
                    if 'default' in config:
                        field.setValue(config['default'][x])

                    if 'description' in config:
                        field.setToolTip(config['description'])

                    self.fields.append(field)
                    widget = createFieldWithLabel(field, axis + ':')
                    self.layout().addWidget(widget)
