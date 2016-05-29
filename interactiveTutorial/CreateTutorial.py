from PyQt4 import QtGui, QtCore
import pprint
import tempfile
from zipfile import ZipFile

import os

from fancywidgets.pyQtBased.FwTabWidget import FwTabWidget 
from fancywidgets.pyQtBased.FwMinimalTextEditor import FwMinimalTextEditor 
from fancywidgets.pyQtBased.Dialogs import Dialogs

from fancytools.os.PathStr import PathStr
#own
from _TutorialBase import TutorialBase


HELP_FILE = PathStr(__file__).dirname().join('GUIDE.pdf')



class CreateTutorial(QtGui.QWidget):
    '''
    Window to create new and modify saved interactive tutorials
    running within the describing program

    >>> from _TestProgram import TestProgram
    >>> app = QtGui.QApplication([])
    
    Our test gui:
    
    >>> win = TestProgram()
    >>> win.show()
    
    The tutorial editor:
    
    >>> createTut = CreateTutorial(win.open, win.save, \
                                   tutorialFolder='testTutorials', \
                                   readonly=False)
    >>> createTut.show()

    >>> app.exec_()
    0
    '''
    def __init__(self, openFunction, saveFunction, 
                 tutorialFolder=None, readonly=False, parent=None):
        '''
        ===============  ===============================================
        Argument         Description
        ===============  ===============================================
        openFunction     Function used to open saved session of a program
                         through calling openFunction([filePath])
        saveFunction     Function used to save a session of a program
                         through calling saveFunction([filePath])
        [OPTIONAL]             
        tutorialFolder   Root directory of the tutorial files
        readonly         [True/False]
                         True: tutorials within [tutorialFolder]
                         cannot be modified
        parent           Parent of this QWidget
        ===============  ===============================================
        '''
        QtGui.QWidget.__init__(self, parent)
        
        self.openFunction = openFunction
        self.saveFunction = saveFunction
        self._lastIndex = 0
        #LAYOUT
        self.setWindowTitle('Tutorial editor')
        self.resize(570,600)
        
        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

        leftlayout = QtGui.QVBoxLayout()
        layout.addLayout(leftlayout)
        
        btn_save = QtGui.QPushButton('save')
        btn_save.clicked.connect(self.save)
        self.edit_name = QtGui.QLineEdit()
        self.edit_name.setPlaceholderText('NEW_TUTORIAL.pyz')

        savelayout = QtGui.QHBoxLayout()
        savelayout.addWidget(btn_save)
        savelayout.addWidget(self.edit_name,1)

        #TUTORIALS STEPS
        self.tabs = FwTabWidget()
        self.tabs.removeTab = self.removeTab
        self.tabs.setTabsClosable(True)
        self.tabs.setTabsRenamable(True)
        self.tabs.defaultTabWidget = lambda: _TutorialStep(self)
        self.tabs.addEmptyTab('Start')

        leftlayout.addLayout(savelayout)
        leftlayout.addWidget(self.tabs)
        self.savedTut = _SavedTutorials(self, tutorialFolder, readonly)
        layout.addWidget(self.savedTut)

        self.tabs.currentChanged.connect(self._changeTab)
      

    def closeEvent(self, evt):
        '''
        deactivate current widget when widget is closed
        '''
        self.tabs.currentWidget().deactivate()
        return evt.accept()
            

    def load(self, path, rootDir):
        '''
        Load a saved tutorial for editing
        '''
        #EXTRACT FILE
        tdir = PathStr(tempfile.mkdtemp('%s_tutorial'))
        ZipFile(path,'r').extractall(path=tdir)
        with open(tdir.join('tutorial.txt'),'r') as f:
            content = eval(f.read())
            
        self.tabs.currentWidget().deactivate()
        #SETUP SESSION
        self.openFunction(tdir.join('session.pyz'))

        self.edit_name.setText(path[len(rootDir)+1:])
        #SETUP TABS
        self.tabs.clear()
        for step in content:
            tab = self.tabs.addEmptyTab(step['name'])
            tab.load(step)

  
    def new(self):
        '''
        start new tutorial (delete old tabs)
        '''
        for c in range(self.tabs.count()-1,-1,-1):
            self.removeTab(c)


    def save(self):
        '''
        save this tutorial to file
        '''
        #GET FILE NAME
        name = unicode(self.edit_name.text())
        if not name:
            name = 'NEW_TUTORIAL.pyz'
            self.edit_name.setText(name)
        path = self.savedTut.dirname.join(name)
        path = path.setFiletype('pyz')
        #OVERRIDE EXISTING?
        if path.exists():
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Override existing?")
            msgBox.addButton('Yes', QtGui.QMessageBox.YesRole)
            msgBox.addButton('No', QtGui.QMessageBox.RejectRole)
            ret = msgBox.exec_()
            if ret != 0:#yes
                return
        #COLLECT TUTORIAL CONTENT
        content = []
        for t in self.tabs:
            l = {}
            l['name'] = unicode(self.tabs.tabText(t))
            content.append(t.save(l))
        #SAVE TO FILE
        with ZipFile(path,'w') as zipFile:
            tdir = PathStr(tempfile.mkdtemp('%s_tutorial'))
            pp = pprint.PrettyPrinter(indent=4)
            #tutorial instructions:
            tutfile = tdir.join('tutorial.txt')
            with open(tutfile ,'w') as f:
                f.write(pp.pformat(content))
            zipFile.write(tutfile, 'tutorial.txt')
            #session:
            sessionfile = tdir.join('session')
            self.saveFunction(sessionfile)
            zipFile.write(sessionfile, 'session.pyz')
   
            tdir.remove()


    def removeTab(self, index):
        '''
        remove a step of the tutorial
        '''
        tab = self.tabs.widget(index)
        if tab:
            tab.chooseWidgetDone()
            tab.deactivate()
            FwTabWidget.removeTab(self.tabs, index)
            if not self.tabs.count():
                self.tabs.addEmptyTab('Start')


    def _changeTab(self, index):
        '''
        change the tutorial step
        '''
        #OLD
        tab = self.tabs.widget(self._lastIndex)
        if tab:  
            tab.chooseWidgetDone()
            tab.deactivate()
        #NEW
        tab = self.tabs.widget(index)
        if tab:
            tab.activate()
        self._lastIndex = index



class _TutorialStep(QtGui.QWidget, TutorialBase):
    '''
    One Step of the tutorial including a marked widget and a text
    '''

    def __init__(self, tutWindow):
        QtGui.QWidget.__init__(self)
        TutorialBase.__init__(self)

        self.tutWindow = tutWindow
        self.mainWindow = None
        self.origPressEvent = None
        #LAYOUT
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        
        self.btn_setWidget = QtGui.QPushButton('Set widget [right click]')
        self.btn_setWidget.clicked.connect(self.chooseWidget)
        
        self.btn_setWidgetDone = QtGui.QPushButton('Done')
        self.btn_setWidgetDone.clicked.connect(self.chooseWidgetDone)
        self.btn_setWidgetDone.setEnabled(False)
        self.btn_setWidgetDone.hide()

        self.editor_text = FwMinimalTextEditor()
        
        self.btn_next = QtGui.QPushButton('Next step')
        self.btn_next.clicked.connect(lambda: tutWindow.tabs.addEmptyTab(
                                            str(tutWindow.tabs.count()+1)))
           
        layout.addWidget(self.btn_setWidget)
        layout.addWidget(self.btn_setWidgetDone)
        layout.addWidget(self.editor_text)
        layout.addWidget(self.btn_next)


    def save(self, l):
        '''
        save content to given dict
        '''
        l['description'] = unicode(self.editor_text.text.toHtml())
        if self.chosenWidget:
            l.update(self.position)
        return l
        
       
 
    def load(self, l):
        '''
        load content from given dict
        '''
        self.editor_text.text.setHtml(l['description'])
        self.getWidgetFromPosition(l)
        self.activate()


    def chooseWidget(self):
        '''
        activate choosing a widget
        '''
        #BUTTONS
        self.btn_setWidgetDone.show()
        self.btn_setWidget.setEnabled(False)
        self.btn_next.setEnabled(False)
        #CONNECT EVERY FOCUS CHANGE
        QtGui.QApplication.instance().focusChanged.connect(self._winFocusChanged)


    def _winFocusChanged(self, old, new):
        '''
        called then the focus on a widget changed
        old - last widget on focus
        new - current widget on focus
        
        doesn't work on QMenu at the moment
        '''
        if new:
            #new can be a widget which is now in focus
            #GET TOP WINDOW
            newWin = new
            while True:
                p = newWin.parent()
                if not p:
                    break
                newWin = p  
            # 1. restore last window mouse click event
            if old == self.mainWindow:
                try:
                    old.mousePressEvent = self.origPressEvent
                except AttributeError:
                    return
            # 2. widget doesn't belong to tutorial:
            if newWin != self.tutWindow:
            # 3. init new window mouse click event
                if newWin != self.mainWindow:
                    self.mainWindow = newWin
                    self.origPressEvent = newWin.mousePressEvent
                    newWin.mousePressEvent = self._getChildWidget
            # 4. focus changed within the same window
                else: 
                    self.markWidget(new)

        
    def _getChildWidget(self, evt):
        '''
        get widget from cursor position
        '''
        self.origPressEvent(evt)
        if evt.button() == QtCore.Qt.RightButton:
            child = self.mainWindow.childAt(evt.pos())
            self.markWidget(child)


    def chooseWidgetDone(self):
        '''
        widget is found - deactivate choosing a widget
        '''
        #BUTTONS
        self.btn_setWidget.setEnabled(True)
        self.btn_next.setEnabled(True)
        self.btn_setWidgetDone.hide()
        #DISCONNECT FROM EVENT
        if self.origPressEvent:
            self.mainWindow.mousePressEvent = self.origPressEvent
        try:
            QtGui.QApplication.instance().focusChanged.disconnect(self._winFocusChanged)
        except TypeError:
            pass #is not connected
        #GET WIDGET POSITION
        self.position = self.getWidgetPosition()

        
    def markWidget(self, w):
        '''
        reset border in last and draw border in current widget
        '''
        self.btn_setWidgetDone.setEnabled(True)
        self.deactivate() #...old
        self.chosenWidget = w
        self.activate() #...new
        

    def getWidgetPosition(self):
        '''
        return the position of the chosen widget used to find it in a later session
        '''
        if not self.chosenWidget:
            return
        pos = []
        l = {}
        #GET POSITION OF WIDGET FROM ITS MAINWINDOW
        child = self.chosenWidget
        if child:
            while True:
                p = child.parent()
                if not p:
                    break
                layout = p.layout
                if callable(layout):
                    layout = layout()
                #position within parent widget: (class_name, position in .layout() )
                pos.append((child.__class__.__name__, layout.indexOf(child) if layout is not None else None))                
                child = p
            pos.append(unicode(child.__class__.__name__))
            pos.append(unicode(child.windowTitle()))
        pos.reverse()
        
        l['childPosFromMainWindow'] = pos

        if isinstance(self.chosenWidget, QtGui.QTreeWidget):
        #GET POSITION OF ITEM IN TREEWIDGET AS (ROW-INDICES, COLUMN)
            item = self.chosenItem
            row_indices = []
            while True:
                p = item.parent()
                if p is None:
                    break
                row_indices.append(p.indexOfChild(item))
                item = p
            row_indices.append(self.chosenWidget.indexFromItem(item).row())
            row_indices.reverse()
            
            l['treeIndices'] = (row_indices, self.chosenWidget.currentColumn())
        return l


class _SavedTutorials(QtGui.QWidget):
    '''
    right side of the create tutorial window with 
    a file tree of saved tutorials
    '''
    def __init__(self, master, tutorialFolder, readonly):
        QtGui.QWidget.__init__(self)  

        self.dialogs = Dialogs()
        
        layout = QtGui.QVBoxLayout()
        #layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout) 
        #BUTTONS
        change = QtGui.QPushButton('Change')
        change.clicked.connect(self.changeDir)
        new = QtGui.QPushButton('New')
        new.clicked.connect(master.new)
        
        self.tutDir = QtGui.QLineEdit()
        self.tutDir.setReadOnly(True)
        
        self.tree =  _TutorialTree(master, readonly)
        tl = QtGui.QHBoxLayout()
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(0)
        
        tl.addWidget(QtGui.QLabel('Root directory'),1) 
        
        btnHelp = QtGui.QPushButton('Help')
        btnHelp.setStyleSheet( " QPushButton {text-decoration: underline color black} ")
        btnHelp.setFlat(True)
        btnHelp.clicked.connect(self._showHelp)
        btnHelp.setFixedWidth(40)
        
        layout.addWidget(btnHelp, 0, QtCore.Qt.AlignRight) 
        layout.addLayout(tl)
        tl.addWidget(self.tutDir)  
        layout.addWidget(change) 
        layout.addWidget(self.tree) 
        layout.addWidget(new) 
         
        self.dirname = PathStr(tutorialFolder)
        if self.dirname:
            self.changeDir(self.dirname)

    def _showHelp(self):
        os.startfile(HELP_FILE)

    def changeDir(self, dirname=None):
        '''
        change the root directory containing the tutorials
        '''
        if dirname is None:
            dirname = self.dialogs.getExistingDirectory()
        if dirname:
            self.dirname = dirname
            self.tutDir.setText(dirname)
            self.tree.changeRootPath(dirname)



class _TutorialTree(QtGui.QTreeView):
    '''
    file tree containing showing saved tutorials
    '''
    def __init__(self, master, readonly):
        QtGui.QTreeView.__init__(self)

        self.master = master
        #SETUP QTREEVIEW
        self.setHeaderHidden(False)
        self.setExpandsOnDoubleClick(False)#connect own function for doubleclick
        self.sortByColumn(0, QtCore.Qt.AscendingOrder)#sort by name
        self.setSortingEnabled(True)
        self.setAnimated(True)#expanding/collapsing animated
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setUniformRowHeights(True)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        #no editing of the items when clicked, rightclicked, doubleclicked:
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        #FILE MODEL
        self.fmodel = QtGui.QFileSystemModel()
        self.fmodel.setReadOnly(readonly)
        self.setModel(self.fmodel)
        self.hideColumn(1)#type
        self.hideColumn(2)#size
        #EVENTS
        self.doubleClicked.connect(self._doubleClicked)
        self.clicked.connect(self._clicked)
        #CONTEXT MENU
        self._menu = _TreeViewContextMenu(self)

 
    def selectionChanged(self,selected, deselected):
        '''
        close change file name dialog if still open
        '''
        for index in deselected.indexes():
            self.closePersistentEditor(index)
        super(_TutorialTree, self).selectionChanged(selected, deselected)


    def createDir(self):
        '''
        create a new directory
        '''
        index = self.currentIndex()
        if not self.fmodel.isDir(index):
            index = index.parent()    
        self.fmodel.mkdir (index, 'new')


    def mousePressEvent(self, event):
        '''
        show right click menu
        '''
        mouseBtn = event.button()
        if mouseBtn == QtCore.Qt.RightButton:
            self._menu.show(event)
        super(_TutorialTree, self).mousePressEvent(event)


    def _doubleClicked(self, index):
        '''
        expand, if directory, 
        open, if tutorial file
        '''
        #if folder->toggle expanding
        if self.fmodel.isDir(index):
            self.setExpanded(index, not self.isExpanded(index) )
        else:
            #ASK: ARE YOU SURE?
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Editing this tutorial closes the current session!")
            msgBox.addButton('Continue', QtGui.QMessageBox.YesRole)
            msgBox.addButton('Cancel', QtGui.QMessageBox.RejectRole)
            ret = msgBox.exec_()
            if ret != 0:#yes
                return 
            self.master.load(PathStr(self.fmodel.filePath(index)), PathStr(self.fmodel.rootPath()))


    def _clicked(self, index):
        '''
        set the filename of the current tutorial to a clicked saved one
        '''
        if not self.fmodel.isDir(index):
            self.master.edit_name.setText(self.fmodel.fileName(index))


    def changeRootPath(self, dirname):
        root = self.fmodel.setRootPath(dirname)
        self.setRootIndex(root)


    def keyPressEvent(self, event):
        '''
        delete file/folder is [Del] is pressed
        '''
        if event.matches(QtGui.QKeySequence.Delete):
            self.deleteCurrentTutorial()
            
            
    def deleteCurrentTutorial(self):
        #ARE YOU SURE?
        msgBox = QtGui.QMessageBox()
        msgBox.setText("Are you sure?")
        msgBox.addButton('Yes', QtGui.QMessageBox.YesRole)
        msgBox.addButton('No', QtGui.QMessageBox.RejectRole)
        ret = msgBox.exec_()
        if ret == 0:#YES
            self.fmodel.remove(self.currentIndex())



class _TreeViewContextMenu(QtGui.QMenu):
    '''
    Context menu with 
     * 'Create directory'
     * 'Rename'
    '''
    def __init__(self, tree):
        QtGui.QMenu.__init__(self) 
        self.tree = tree   
        self.addAction('Create directory').triggered.connect(self.tree.createDir)
        self.a_rename = self.addAction('Rename')
        self.a_rename.triggered.connect(lambda:
                        self.tree.openPersistentEditor(self.tree.currentIndex()))

        self.addAction('Delete').triggered.connect(self.tree.deleteCurrentTutorial)


    def show(self, evt):
        self.popup(evt.globalPos())




if __name__ == '__main__':
    import doctest
    doctest.testmod()