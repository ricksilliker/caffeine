import platform

from PySide2 import QtWidgets, QtCore, QtGui

import blueprints


class RigHierarchyWidget(QtWidgets.QWidget):
    rigComponentAdded = QtCore.Signal()
    selectionChanged = QtCore.Signal(object)
    _instance = []

    ObjectRole = QtCore.Qt.UserRole + 1
    TypeRole = QtCore.Qt.UserRole + 2

    def __init__(self, blueprintPath, parent=None):
        super(RigHierarchyWidget, self).__init__(parent=parent)

        self._instance.append(self)
        self._blueprintHierarchy = blueprints.BlueprintHierarchy()
        self._callbacks = dict()

        self._initMain()

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        headerLayout = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(headerLayout)

        self.addMenu = QtWidgets.QMenu()
        self._availableBlueprints = blueprints.loadAvailableByTitle(blueprintPath)
        for name, bp in self._availableBlueprints.items():
            self.addMenu.addAction(name, lambda x=name: self.addBlueprintCallback(name))

        self.addButton = QtWidgets.QPushButton('Add')
        self.addButton.setMenu(self.addMenu)
        headerLayout.addWidget(self.addButton)

        self.rigHierarchyModel = QtGui.QStandardItemModel()

        self.rigHierarchyView = QtWidgets.QTreeView()
        self.rigHierarchyView.setModel(self.rigHierarchyModel)
        mainLayout.addWidget(self.rigHierarchyView)

        self.rigComponentAdded.connect(self.refreshRigHierarchyView)
        self.rigHierarchyView.clicked.connect(self.selectionChangedCallback)

    @classmethod
    def run(cls, blueprintPath, parent=None):
        widget = cls(blueprintPath, parent=parent)

        widget.setWindowFlags(widget.windowFlags() | QtCore.Qt.Window)

        if platform.system() == 'Darwin':
            # MacOS is special, and the QtCore.Qt.Window flag does not sort the windows properly,
            # so QtCore.Qt.Tool is added.
            widget.setWindowFlags(widget.windowFlags() | QtCore.Qt.Dialog)

        # Center the widget with Maya's main window.
        if parent is not None:
            widget.move(parent.frameGeometry().center() - QtCore.QRect(QtCore.QPoint(), widget.sizeHint()).center())

        widget.show()

        return widget

    @classmethod
    def findInstance(cls):
        for x in cls._instance:
            if x.isVisible():
                return x

    def _initMain(self):
        self.setWindowTitle('Rig Hierarchy')
        self.setObjectName('RigHierarchyWidget')

    def setCallback(self, name, cb):
        if name in self._callbacks:
            self._callbacks.append(cb)
        else:
            self._callbacks[name] = [cb]

    def refreshRigHierarchyView(self):
        self.rigHierarchyModel.clear()
        self._blueprintHierarchy.clear()
        callbacks = self._callbacks.get('collectBlueprints', None)
        if callbacks is None:
            return
        for cb in callbacks:
            cb(self._blueprintHierarchy)

        items = []
        for bp in self._blueprintHierarchy.blueprints:
            items.append(self.addBlueprintItem(bp))

        for i, item in enumerate(items):
            bp = self._blueprintHierarchy.blueprints[i]
            childIndices = bp['children']
            for index in childIndices:
                item.appendRow(items[index])
            if not childIndices:
                self.rigHierarchyModel.appendRow(item)

    def selectionChangedCallback(self, modelIndex):
        blueprintData = self.rigHierarchyModel.data(modelIndex, RigHierarchyWidget.ObjectRole)
        self.selectionChanged.emit(blueprintData)

    def addBlueprintItem(self, blueprintData):
        item = QtGui.QStandardItem(blueprintData['blueprint'].name)
        item.setData(blueprintData['blueprint'], RigHierarchyWidget.ObjectRole)
        item.setData(blueprintData['blueprint'].componentType, RigHierarchyWidget.TypeRole)
        return item

    def addBlueprintCallback(self, name):
        bp = self._availableBlueprints[name]
        bp.create()
        self.rigComponentAdded.emit()
