from PySide2 import QtWidgets, QtCore, QtGui

import widgets
import actions


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

        self.newActionsWidget = NewActionsWidget()
        self.layout().addWidget(self.newActionsWidget)

        self.actionOutlinerWidget = ActionOutlinerWidget()
        self.layout().addWidget(self.actionOutlinerWidget)
        self.actionOutlinerWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

        self.actionSettingsWidget = ActionSettingsWidget()
        self.layout().addWidget(self.actionSettingsWidget)

        self.runWidget = RunnerWidget()
        self.layout().addWidget(self.runWidget)

    def sizeHint(self):
        return QtCore.QSize(300, 450)


class NewActionsWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(NewActionsWidget, self).__init__(parent=parent)

        self.layout().setDirection(QtWidgets.QBoxLayout.LeftToRight)

        self.generalActionsButton = QtWidgets.QToolButton()
        self.generalActionsButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.layout().addWidget(self.generalActionsButton)
        
        self.jointActionsButton = QtWidgets.QToolButton()
        self.jointActionsButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.layout().addWidget(self.jointActionsButton)
        
        self.deformActionsButton = QtWidgets.QToolButton()
        self.deformActionsButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.layout().addWidget(self.deformActionsButton)

        self.utilActionsButton = QtWidgets.QToolButton()
        self.utilActionsButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.layout().addWidget(self.utilActionsButton)

        self.loadAvailableActions()

    def createActionMenu(self, categoryActions):
        menu = QtWidgets.QMenu(self)

        for a in categoryActions:
            menu.addAction(a.title)
        
        return menu

    def loadAvailableActions(self):
        allActions = actions.loadDefaultActions()

        generalMenu = self.createActionMenu([a for a in allActions if a.category == 'general'])
        self.generalActionsButton.setMenu(generalMenu)

        utilMenu = self.createActionMenu([a for a in allActions if a.category == 'utils'])
        self.utilActionsButton.setMenu(utilMenu)


class ActionOutlinerWidget(QtWidgets.QTreeWidget):
    def __init__(self, parent=None):
        super(ActionOutlinerWidget, self).__init__(parent=parent)

        self.setHeaderHidden(True)

        testItem = QtWidgets.QTreeWidgetItem()
        testItem.setText(0, 'Test Item')
        self.addTopLevelItem(testItem)

    def sizeHint(self):
        return QtCore.QSize(300, 150)


class ActionSettingsWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(ActionSettingsWidget, self).__init__(parent=parent)

        self.actionFormWidget = ActionWidget()

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


class ActionWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(ActionWidget, self).__init__(parent=parent)

        self.actionHeaderWidget = ActionHeaderWidget()
        self.layout().addWidget(self.actionHeaderWidget)

        self.actionPropertiesWidget = ActionPropertiesWidget()
        self.layout().addWidget(self.actionPropertiesWidget)

    def loadFromAction(self, actionData):
        self.actionHeaderWidget.clean()
        self.actionPropertiesWidget.clean()

        self.actionHeaderWidget.load(actionData)
        self.actionPropertiesWidget.load(actionData)

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

    def clean(self):
        self.titleField.setText('')

    def load(self, actionData):
        self.titleField.setText(actionData['title'])


class ActionPropertiesWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(ActionPropertiesWidget, self).__init__(parent=parent)

        self.formLayout = QtWidgets.QFormLayout()
        self.layout().addLayout(self.formLayout)

    def clean(self):
        for rowIndex in reversed(range(self.formLayout.rowCount)):
            self.formLayout.removeRow(rowIndex)

    def load(self, actionData):
        for p in actionData.props:
            fieldWidget = widgets.getDataWidget(p.config)
            fieldWidget.setCurrentValue(p.currentValue)
            self.formLayout.addRow(fieldWidget.displayName, fieldWidget)
        

class RunnerWidget(widgets.AbstractWidget):
    def __init__(self, parent=None):
        super(RunnerWidget, self).__init__(parent=parent)

        self.layout().setDirection(QtWidgets.QBoxLayout.LeftToRight)

        self.buildButton = QtWidgets.QPushButton('Build')
        self.layout().addWidget(self.buildButton)

        self.buildOptionsButton = QtWidgets.QToolButton()
        self.buildOptionsButton.setMenu(self.getMenu())
        self.buildOptionsButton.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.layout().addWidget(self.buildOptionsButton)

    def getMenu(self):
        menu = QtWidgets.QMenu(self)
        menu.addAction('Build in Background')

        return menu

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
