import sys
import logging
import platform

from maya import OpenMayaUI
from shiboken2 import wrapInstance
from PySide2 import QtWidgets, QtCore, QtGui

from caffeine import panels
import core


LOG = logging.getLogger(__name__)


def mayaMainWindow():
    OpenMayaUI.MQtUtil.mainWindow()
    ptr = OpenMayaUI.MQtUtil.mainWindow()

    return wrapInstance(long(ptr), QtWidgets.QWidget)


def showRigHierarchyPanel():
    parent = mayaMainWindow()
    widget = panels.RigHierarchyWidget.run(core.getDefaultBlueprintPath(), parent)
    widget.setCallback('collectBlueprints', core.getActiveBlueprints)
    widget.refreshRigHierarchyView()


class InspectorWidget(QtWidgets.QWidget):
    selectionChanged = QtCore.Signal()

    def __init__(self, parent=None):
        super(InspectorWidget, self).__init__(parent=parent)

        self._childrenComponentWidgets = []

        self._initMain()

        mainLayout = QtWidgets.QVBoxLayout(self)
        self._mainLayout = mainLayout
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        self.selectionChanged.connect(self.refreshInspectorView)

    def sizeHint(self):
        return QtCore.QSize(300, 400)

    @classmethod
    def run(cls):
        app = mayaMainWindow()

        widget = cls(parent=app)

        widget.setWindowFlags(widget.windowFlags() | QtCore.Qt.Window)

        if platform.system() == 'Darwin':
            # MacOS is special, and the QtCore.Qt.Window flag does not sort the windows properly,
            # so QtCore.Qt.Tool is added.
            widget.setWindowFlags(widget.windowFlags() | QtCore.Qt.Dialog)

        # Center the widget with Maya's main window.
        widget.move(app.frameGeometry().center() - QtCore.QRect(QtCore.QPoint(), widget.sizeHint()).center())

        rigHierarchyWidget = RigHierarchyWidget.findInstance()
        if rigHierarchyWidget is not None and rigHierarchyWidget.isVisible():
            rigHierarchyWidget.selectionChanged.connect(widget.selectionChangedCallback)
            widget.refreshInspectorView()

        widget.show()

        return widget

    def _initMain(self):
        self.setWindowTitle('Inspector')
        self.setObjectName('InspectorWidget')

    def clean(self):
        while self._mainLayout.count():
            layoutItem = self._mainLayout.takeAt(0)
            layoutItem.widget().deleteLater()

    def refreshInspectorView(self):
        self.clean()
        for dataWidget in self._childrenComponentWidgets:
            self._mainLayout.addWidget(dataWidget)

    def selectionChangedCallback(self, data):
        self._childrenComponentWidgets = []
        widget = DataWidget(data['nodeType'], data['node'])
        self._childrenComponentWidgets.append(widget)
        self.refreshInspectorView()


class CollapseWidget(QtWidgets.QWidget):
    completed = QtCore.Signal(bool)

    def __init__(self, title, parent=None):
        super(CollapseWidget, self).__init__(parent=parent)

        self.toggleButton = QtWidgets.QToolButton(
            text=title, checkable=True, checked=False
        )
        self.toggleButton.setStyleSheet("QToolButton { border: none; }")
        self.toggleButton.setToolButtonStyle(
            QtCore.Qt.ToolButtonTextBesideIcon
        )
        self.toggleButton.setArrowType(QtCore.Qt.RightArrow)
        self.toggleButton.setChecked(False)
        self.toggleButton.released.connect(self.onReleased)

        self.contentArea = QtWidgets.QScrollArea(
            maximumHeight=0, minimumHeight=0
        )
        self.contentArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.contentArea.setWidgetResizable(True)
        self.contentArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.contentArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.contentArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.contentArea.setFrameShape(QtWidgets.QFrame.Box)

        headerLayout = QtWidgets.QHBoxLayout()
        headerLayout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        headerLayout.setSpacing(0)
        headerLayout.setContentsMargins(0, 0, 0, 0)
        headerLayout.addWidget(self.toggleButton)

        lay = QtWidgets.QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(headerLayout)
        lay.addWidget(self.contentArea)

    def expand(self):
        self.toggleButton.setChecked(True)
        self.onReleased()

    def collapse(self):
        self.toggleButton.setChecked(False)
        self.onReleased()

    def onReleased(self):
        checked = self.toggleButton.isChecked()

        if not checked:
            self.toggleButton.setArrowType(QtCore.Qt.RightArrow)
            self.contentArea.setMaximumHeight(self.collapsedHeight)
            self.setMaximumHeight(self.collapsedHeight)
            self.contentArea.setFrameShape(QtWidgets.QFrame.NoFrame)
            self.contentArea.hide()
        else:
            self.toggleButton.setArrowType(QtCore.Qt.DownArrow)
            self.contentArea.setMaximumHeight(self.contentHeight + self.collapsedHeight)
            self.setMaximumHeight(self.contentHeight + self.collapsedHeight)
            self.contentArea.setFrameShape(QtWidgets.QFrame.Box)
            self.contentArea.show()

    @property
    def collapsedHeight(self):
        return self._collapsedHeight

    @collapsedHeight.setter
    def collapsedHeight(self, value):
        self._collapsedHeight = value

    @property
    def contentHeight(self):
        return self._contentHeight

    @contentHeight.setter
    def contentHeight(self, value):
        self._contentHeight = value

    def setContentLayout(self, layout):
        oldWidget = self.contentArea.widget()
        if oldWidget is not None:
            oldWidget.deleteLater()

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.contentArea.setWidget(widget)

        self.collapsedHeight = self.sizeHint().height() - self.contentArea.maximumHeight()
        self.contentHeight = layout.sizeHint().height()


class DataWidget(QtWidgets.QWidget):
    def __init__(self, title, componentData):
        super(DataWidget, self).__init__()
        self._title = title
        self._dataObject = componentData

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        contentLayout = QtWidgets.QFormLayout()
        for field in self._dataObject.fields:
            fieldWidgetType = FieldWidgetFactory.getFieldWidget(field.dataType)
            contentLayout.addRow(field.name, fieldWidgetType())

        self.frameWidget = CollapseWidget(title=self._title)
        self.frameWidget.setContentLayout(contentLayout)
        mainLayout.addWidget(self.frameWidget)


class FieldWidgetFactory(QtWidgets.QWidget):
    def __init__(self):
        super(FieldWidgetFactory, self).__init__()
        mainLayout = QtWidgets.QVBoxLayout(self)
        self._mainLayout = mainLayout
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

    @staticmethod
    def getFieldWidgets():
        widgets = {}
        for x in FieldWidgetFactory.__subclasses__():
            widgets[x.dataType] = x
        return widgets

    @staticmethod
    def getFieldWidget(dataType):
        return FieldWidgetFactory.getFieldWidgets().get(dataType, NullFieldWidget)


class StringFieldWidget(FieldWidgetFactory):
    dataType = 'str'

    def __init__(self, propData):
        self._propData = propData
        super(StringFieldWidget, self).__init__()
        self.field = QtWidgets.QLineEdit('')
        self._mainLayout.addWidget(self.field)

    def load(self):
        data = self._propData.value
        self.field.setText(data)

    def save(self):
        self._propData.value = str(self.field.text())


class BoolFieldWidget(FieldWidgetFactory):
    dataType = 'bool'

    def __init__(self, propData):
        self._propData = propData
        super(BoolFieldWidget, self).__init__()
        self.field = QtWidgets.QCheckBox('')
        self._mainLayout.addWidget(self.field)

    def load(self):
        data = self._propData.value
        self.field.setChecked(data)

    def save(self):
        self._propData.value = self.field.isChecked()


class NullFieldWidget(FieldWidgetFactory):
    dataType = 'null'

    def __init__(self):
        super(NullFieldWidget, self).__init__()
        self.field = QtWidgets.QLabel('No valid value')
        self._mainLayout.addWidget(self.field)
