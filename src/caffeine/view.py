from PySide2 import QtWidgets, QtCore, QtGui

import widgets


class MainWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent=parent)
        self.setWindowTitle('Caffeine Settings')

        tabWidget = QtWidgets.QTabWidget()
        # tabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        # tabWidget.tabBar().setStyle(TabStyle())
        self.layout().addWidget(tabWidget)

        buildWidget = BuildWidget()
        tabWidget.addTab(buildWidget, 'Build')

        consoleWidget = ConsoleWidget()
        tabWidget.addTab(consoleWidget, 'Console')

    def sizeHint(self):
        return QtCore.QSize(300, 450)


class TabStyle(QtWidgets.QCommonStyle):    
    def sizeFromContents(self, t, option, size, widget):
        size = super(TabStyle, self).sizeFromContents(t, option, size, widget)
        if t == QtWidgets.QStyle.CT_TabBarTab:
            size.transpose()
        
        return size

    def drawControl(self, elem, option, painter, widget):
        if elem == QtWidgets.QStyle.CE_TabBarTabLabel:
            opt = QtWidgets.QStyleOptionTab()
            widget.initStyleOption(opt, widget.currentIndex())
            opt.shape = QtWidgets.QTabBar.RoundedNorth
            super(TabStyle, self).drawControl(elem, opt, painter, widget)
        else:
            super(TabStyle, self).drawControl(elem, option, painter, widget)


class BuildWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(BuildWidget, self).__init__(parent=parent)

        self.executionHierarchyWidget = ExecutionHierarchyWidget()
        self.layout().addWidget(self.executionHierarchyWidget)
        self.executionHierarchyWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        self.actionSettingsWidget = ActionSettingsWidget()
        self.layout().addWidget(self.actionSettingsWidget)

        self.runWidget = RunnerWidget()
        self.layout().addWidget(self.runWidget)

    def sizeHint(self):
        return QtCore.QSize(300, 450)


class ExecutionHierarchyWidget(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(ExecutionHierarchyWidget, self).__init__(parent=parent)

        testItem = QtWidgets.QListWidgetItem('Test Item')
        self.addItem(testItem)

    def sizeHint(self):
        return QtCore.QSize(300, 150)


class ActionSettingsWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(ActionSettingsWidget, self).__init__(parent=parent)

        self.actionFormWidget = ActionsFormWidget()
        self.actionFormWidget.addActionWidget(action={})

        scrollArea = QtWidgets.QScrollArea()
        scrollArea.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        scrollArea.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        scrollArea.setFrameShape(QtWidgets.QFrame.Box)
        scrollArea.setWidget(self.actionFormWidget)

        self.layout().addWidget(scrollArea)

    def sizeHint(self):
        return QtCore.QSize(300, 300)


class ActionsFormWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(ActionsFormWidget, self).__init__(parent=parent)

    def addActionWidget(self, action):
        widget = ActionWidget.fromData(action)
        self.layout().addWidget(widget)


class ActionWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(ActionWidget, self).__init__(parent=parent)

        self.actionHeaderWidget = ActionHeaderWidget()
        self.layout().addWidget(self.actionHeaderWidget)

        self.actionPropertiesWidget = ActionPropertiesWidget()
        self.layout().addWidget(self.actionPropertiesWidget)

    @classmethod
    def fromData(cls, actionData):
        widget = cls()
        widget.actionPropertiesWidget.loadFromData(data=actionData)

        return widget


class ActionHeaderWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(ActionHeaderWidget, self).__init__(parent=parent)

        self.layout().setDirection(QtWidgets.QBoxLayout.LeftToRight)

        self.titleField = QtWidgets.QLabel('Empty Action Title')
        self.layout().addWidget(self.titleField)

        self.debugButton = QtWidgets.QPushButton('[D]')
        self.layout().addWidget(self.debugButton)

        self.enableButton = QtWidgets.QPushButton('[E]')
        self.layout().addWidget(self.enableButton)

        self.settingsButton = QtWidgets.QPushButton('[S]')
        self.layout().addWidget(self.settingsButton)


class ActionPropertiesWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(ActionPropertiesWidget, self).__init__(parent=parent)

        self.formLayout = QtWidgets.QFormLayout()
        self.layout().addLayout(self.formLayout)

    def loadFromData(self, data):
        self.formLayout.addRow('Test Item', QtWidgets.QPushButton('Click Me'))


class RunnerWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(RunnerWidget, self).__init__(parent=parent)

        self.layout().setDirection(QtWidgets.QBoxLayout.LeftToRight)

        self.buildButton = QtWidgets.QPushButton('Build')
        self.layout().addWidget(self.buildButton)

        self.buildOptionsButton = QtWidgets.QToolButton()
        self.layout().addWidget(self.buildOptionsButton)

    def sizeHint(self):
        return QtCore.QSize(300, 50)


class ConsoleWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(ConsoleWidget, self).__init__(parent=parent)

        self.browser = QtWidgets.QTextBrowser()
        self.browser.setFontFamily('Courier')
        self.browser.setReadOnly(True)
        self.browser.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.layout().addWidget(self.browser)
