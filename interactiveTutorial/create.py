'''
Created on 3 Sep 2014

@author: elkb4
'''

from PyQt4 import QtGui, QtCore
from fancywidgets.pyQtBased.FwTabWidget import FwTabWidget 
from fancywidgets.pyQtBased.FwMinimalTextEditor import FwMinimalTextEditor 

import inspect



class _TutorialPage(QtGui.QWidget):

    def __init__(self, mainwindow):
        QtGui.QWidget.__init__(self)
        self._mainwindow = mainwindow
        self.cursor = QtGui.QCursor()

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        
        
        self.editor_text = FwMinimalTextEditor()
        
        self.btn_setWidget = QtGui.QPushButton('set widget')
        self.btn_setWidget.clicked.connect(self.chooseWidget)
        
        self.widget = QtGui.QLabel()
        
        self.combo_setCondition = QtGui.QComboBox()

        self.combo_setCondition.hide()
        
        self.combo_setNext = QtGui.QComboBox()
        self.combo_setCondition.addItems(['next page', 'exit'])

        self.combo_setNext.hide()
      
        
        layout.addWidget(self.editor_text)
        layout.addWidget(self.btn_setWidget)
        layout.addWidget(self.widget)
        layout.addWidget(self.combo_setCondition)
        layout.addWidget(self.combo_setNext)


#     def _addToClicked(self, parent):
#         for ch in parent.children():
#            # if isinstance(ch, QtGui.QWidget):
#             print ch#.name()
#             clicked = getattr(ch, 'clicked', None) 
#             if clicked:
#                 print 55
#                 clicked.connect(self._y)
#             self._addToClicked(ch)


    def chooseWidget(self):
        self.btn_setWidget.setEnabled(False)
        self.origPressEvent = self._mainwindow.mousePressEvent
        self._mainwindow.mousePressEvent = self._getChildWidget
        self._mainwindow.grabMouse()
        

        
    def _getChildWidget(self, evt):
        child = self._mainwindow.childAt(evt.pos())
        nameFn = getattr(child, 'name', None)
        if nameFn:
            text = nameFn()
        else:
            text = str(child)
        self.widget.setText(text)
        
        classes = [x[1] for x in inspect.getmembers(child)]# if isinstance(x, QtCore.pyqtSignal)]
        signals = [x for x in classes if type(x) in (QtCore.pyqtSignal, QtCore.pyqtBoundSignal)]

        signal_names = [x.__class__.__name__ for x in signals]
        
        self.combo_setCondition.clear()
        self.combo_setCondition.addItems(signal_names)
        
        self.combo_setCondition.show()
        self.combo_setNext.show()

        #reset state
        self._mainwindow.mousePressEvent = self.origPressEvent
        self._mainwindow.mousePressEvent(evt)
        self._mainwindow.releaseMouse()
        self.btn_setWidget.setEnabled(True)
        



class _TutorialTree(QtGui.QTreeView):
    def __init__(self):
        QtGui.QTreeView.__init__(self)

        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        model = QtGui.QStandardItemModel()
        #model.setHorizontalHeaderLabels(['col1', 'col2', 'col3'])
        self.setModel(model)
        self.setUniformRowHeights(True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# populate data
        for i in range(3):
            parent1 = QtGui.QStandardItem('Family {}. Some long status text for sp'.format(i))
            for j in range(3):
                child1 = QtGui.QStandardItem('Child {}'.format(i*3+j))
                child2 = QtGui.QStandardItem('row: {}, col: {}'.format(i, j+1))
                child3 = QtGui.QStandardItem('row: {}, col: {}'.format(i, j+2))
                parent1.appendRow([child1, child2, child3])
            model.appendRow(parent1)
            # span container columns
            self.setFirstColumnSpanned(i, self.rootIndex(), True)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# expand third container
#         index = model.indexFromItem(parent1)
#         self.expand(index)
# # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# # select last row
#         selmod = self.selectionModel()
#         index2 = model.indexFromItem(child3)
#         selmod.select(index2, QtGui.QItemSelectionModel.Select|QtGui.QItemSelectionModel.Rows)
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




class CreateTutorial(FwTabWidget):
    def __init__(self, mainwindow):
        #self._mainwindow = mainwindow
        FwTabWidget.__init__(self)
        self.setWindowTitle('CREATE')
        self.resize(500,600)
        
        layout = QtGui.QHBoxLayout()
        self.setLayout(layout)

        leftlayout = QtGui.QVBoxLayout()
        layout.addLayout(leftlayout)
        
        btn_save = QtGui.QPushButton('save')

        tabs = FwTabWidget()
        tabs.setTabsAddable(True)
        tabs.setTabsClosable(True)
        tabs.setTabsRenamable(True)
        tabs.defaultTabWidget = lambda: _TutorialPage(mainwindow)
        tabs.addEmptyTab('Start')

        leftlayout.addWidget(btn_save)
        leftlayout.addWidget(tabs)
        
        tutTree = _TutorialTree()
        layout.addWidget(tutTree)





if __name__ == '__main__':
    import sys
    app = QtGui.QApplication([])
    win = QtGui.QMainWindow()
    w = QtGui.QWidget()
    win.setCentralWidget(w)
    l = QtGui.QHBoxLayout()
    w.setLayout(l)
    l.addWidget(QtGui.QPushButton())
    l.addWidget(QtGui.QPushButton())
    l.addWidget(QtGui.QPushButton())
    menu = QtGui.QMenuBar()
    win.setMenuBar(menu)
    m1 = QtGui.QMenu('one')
    m1.addAction('two')
    menu.addMenu(m1)
    l.addWidget(QtGui.QLineEdit())

    
    

    win.show()
    
    tut = CreateTutorial(win)
    tut.show()
    
    sys.exit(app.exec_())


        