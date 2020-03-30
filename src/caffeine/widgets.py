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
            widget.setWindowFlags(widget.windowFlags() | QtCore.Qt.Dialog)
        
        # Center the widget with Maya's main window.
        widget.move(app.frameGeometry().center() - QtCore.QRect(QtCore.QPoint(), widget.sizeHint()).center())
        
        widget.show()

        return widget


def getDataWidget(config):
    dataType = config.get('type', None)

    if dataType == 'string':
        field = StringPropertyWidget(config)
    elif dataType == 'float':
        field = FloatPropertyWidget(config)
    elif dataType == 'array':
        field = ArrayPropertyWidget(config)
    else:
        field = None

    return field


class PropertyWidget(AbstractWidget):
    propertyValueChanged = QtCore.Signal(object)

    def __init__(self, data, parent=None):
        super(PropertyWidget, self).__init__(parent=parent)

        self._data = dict()
        self._data.update(data)

        if 'config' in self._data:
            self.configure()

            if 'description' in config:
                self.setToolTip(config['description'])

    @property
    def displayName(self):
        return self._data['name']

    @property
    def dataBlock(self):
        return self._data

    def configure(self):
        LOG.exception('property configure method not implemented')

    def on_data_changed(self, value):
        requestBody = dict(widgetValue=value)
        self.propertyValueChanged.emit(requestBody)

    def configureEnumField(self, config):
        field = QtWidgets.QComboBox()
        field.addItems(config['enum'])
        
        if 'default' in config:
            for i in range(field.count()):
                if field.itemText(i) == config['default']:
                    field.setCurrentIndex(i)
                    break

        field.currentTextChanged(self.on_data_changed)

        return field

    def configureFloatField(self, config):
        field = QtWidgets.QDoubleSpinBox()
        field.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)

        if 'minimum' in config:
            field.setMinimum(config['minimum'])

        if 'maximum' in config:
            field.setMaximum(config['maximum'])

        if 'default' in config:
            field.setValue(config['default'])

        field.valueChanged.connect(self.on_data_changed)

        return field

    def configureStringField(self, config):
        field = QtWidgets.QLineEdit()

        if 'pattern' in config:
            regex = QtCore.QRegExp(config['pattern'])
            regexValidator = QtGui.QRegExpValidator(regex)
            field.setValidator(regexValidator)

        if 'default' in config:
            field.setText(config['default'])
        
        field.textChanged.connect(self.on_data_changed)

        return field


class StringPropertyWidget(PropertyWidget):
    def __init__(self, data, parent=None):
        super(StringPropertyWidget, self).__init__(parent=parent)

    def configure(self):
        config = self._data['config']

        if 'enum' in config:
            field = self.configureEnumField(config)
        else:
            field = self.configureStringField(config)

        self.layout().addWidget(field)


class FloatPropertyWidget(PropertyWidget):
    def __init__(self, config, parent=None):
        super(FloatPropertyWidget, self).__init__(parent=parent)

    def configure(self):
        config = self._data['config']

        if 'enum' in config:
            self.configureEnumField(config)
        else:
            self.configureFloatField(config)

        self.layout().addWidget(field)


class ArrayPropertyWidget(PropertyWidget):
    def __init__(self, config, parent=None):
        super(ArrayPropertyWidget, self).__init__(parent=parent)

    def createFieldWithLabelWidget(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(widget)
        layout.setAlignment(QtCore.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        return widget

    def configure(self):
        config = self._data['config']

        if 'semanticType' in config:
            if config['semanticType'] == 'VEC3':
                widget = createFieldWithLabelWidget()

                for x, axis in enumerate(['X', 'Y', 'Z']):
                    item_config = dict()
                    item_config.update(config)
                    item_config.update(config['items'])

                    if 'default' in item_config:
                        item_config['default'] = item_config['default'][x]

                    if 'enum' in config:
                        field = self.configureEnumField(item_config)
                    elif item_config['type'] == 'string':
                        field = self.configureStringField(item_config)
                    elif item_config['type'] == 'float':
                        field = self.configureFloatField(item_config)
                    else:
                        continue

                    widget.layout().addRow(axis + ':', field)
