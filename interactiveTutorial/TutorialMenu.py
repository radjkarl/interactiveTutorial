from PyQt4 import QtGui

from fancytools.os.PathStr import PathStr

#own
from RunTutorial import RunTutorial
from CreateTutorial import CreateTutorial



class TutorialMenu(QtGui.QMenu):
    '''
     A QMenu containing
     
    * 'Run' - listing all saved tutorials to run
    * 'Create/Edit' - open the tutorial editor

    >>> from _TestProgram import TestProgram
    >>> app = QtGui.QApplication([])
    
    Our test gui:
    
    >>> win = TestProgram()
    
    Add a tutorial menu the the menubar of our gui: 
    [Note: If you use this within a class you have to attach the menu to e.g. self!]
    
    >>> menu = TutorialMenu( tutorialFolder='testTutorials',\
                             openFunction=win.open,\
                             saveFunction=win.save )
    >>> _ = win.menuBar().addMenu(menu)

    >>> win.show()
    >>> app.exec_() 
    0
    '''
    def __init__(self, tutorialFolder, openFunction, saveFunction, 
                 title='Tutorial', readonly=False, **kwargs):
        '''
        ===============  ===============================================
        Argument         Description
        ===============  ===============================================
        tutorialFolder   Root directory of the tutorial files

        openFunction     Function used to open saved session of a program
                         through calling openFunction([filePath])
        saveFunction     Function used to save a session of a program
                         through calling saveFunction([filePath])
        [OPTIONAL] 
        title            the name of the QMenu            
        readonly         [True/False]
                         True: tutorials within [tutorialFolder]
                         cannot be modified
        ===============  ===============================================
        '''
        QtGui.QMenu.__init__(self, title, **kwargs)
        
        self.tutorial = None
        self.tutorialFolder = PathStr(tutorialFolder)
        self.openFunction = openFunction 
        self.saveFunction = saveFunction
        self.readonly = readonly
        #SUB STRUCTURE
        self.m_run = self.addMenu('Run')
        self.m_run.aboutToShow.connect(self._buildRunTutorialMenu)
        self.addAction('Create/Edit').triggered.connect(self.createTutorial)


    def runTutorial(self, path):
        '''
        Close old and run a new tutorial
        '''
        #ASK: ARE YOU SURE?
        msgBox = QtGui.QMessageBox()
        msgBox.setText("Starting this tutorial closes the current session!")
        msgBox.addButton('Continue', QtGui.QMessageBox.YesRole)
        msgBox.addButton('Cancel', QtGui.QMessageBox.RejectRole)
        ret = msgBox.exec_()
        if ret != 0:#yes
            return
        #close old tutorial
        if self.tutorial:
            self.tutorial.close()
        self.tutorial = RunTutorial(path, self.openFunction)
        self.tutorial.show()


    def createTutorial(self):
        '''
        Close old tutorial and open tutorial editor
        '''
        if self.tutorial and self.tutorial.isVisible():
            #ASK: ARE YOU SURE?
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Creating/Editing a tutorial closes the current tutorial!")
            msgBox.addButton('Continue', QtGui.QMessageBox.YesRole)
            msgBox.addButton('Cancel', QtGui.QMessageBox.RejectRole)
            ret = msgBox.exec_()
            if ret != 0:#yes
                return
            self.tutorial.close()
            
        self.tutorial = CreateTutorial( 
                    self.openFunction, 
                    self.saveFunction, 
                    self.tutorialFolder,
                    self.readonly)
        self.tutorial.show()


    def _buildRunTutorialMenu(self):
        '''
        Build a nested menu structure showing all tutorial files and sub directories
        '''
        self.m_run.clear()
        def build(menu, folder):
            for f in folder:
                c = folder.join(f)
                if c.isfile() and c.filetype() == 'pyz':
                    menu.addAction(f).triggered.connect(lambda checked, c=c: self.runTutorial(c))
                else:
                    m = menu.addMenu(f)
                    build(m,c)
        build(self.m_run, self.tutorialFolder)



if __name__ == '__main__':
    import doctest
    doctest.testmod() 