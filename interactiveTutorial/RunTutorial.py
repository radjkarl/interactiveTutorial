from PyQt4 import QtGui, QtCore
import tempfile
from zipfile import ZipFile

from fancytools.os.PathStr import PathStr
#own
from _TutorialBase import TutorialBase



class RunTutorial(QtGui.QWidget, TutorialBase):
    '''
    Always-on-top-window to control (Restart, Next, Previous)
    the chosen tutorial

    >>> from _TestProgram import TestProgram
    >>> app = QtGui.QApplication([])
    
    Our test gui:
    
    >>> win = TestProgram()
    >>> win.show()
    
    First tutorial file in tutorial folder:
    
    >>> p = PathStr('testTutorials')
    >>> tut_file = p.join(p.listdir()[0])
    
    The Tutorial widget:
    
    >>> tut = RunTutorial(tut_file, win.open)
    >>> tut.show()

    >>> app.exec_()
    0
    '''

    def __init__(self, path, openFunction, parent=None):
        '''
        =============    =========================================
        Argument         Description
        =============    =========================================
        path             Path of the tutorial file to open
        openFunction     Function used to open saved session of a program
                         through calling openFunction([filePath])           
        [OPTIONAL]
        parent           Parent of this QWidget
        =============    =========================================
        '''

        QtGui.QWidget.__init__(self, parent)
        TutorialBase.__init__(self)

        sessionFile, content = self.unpackFile(path)
        self.initSession = lambda: openFunction(sessionFile)

        #this window always on top
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_MediaPlay))

        path = PathStr(path)
        self.setWindowTitle('Tutorial: %s' %path.basename().split('.')[0])
        
        # START BUTTON
        start = QtGui.QPushButton('Restart')
        start.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_MediaPlay))
        start.clicked.connect(self.restart)
        # <- AND -> BUTTON
        self.btn_previous = QtGui.QPushButton('Previous')
        self.btn_previous.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_MediaSeekBackward))
        self.btn_previous.clicked.connect(self.previousStep)
        self.btn_previous.setEnabled(False)
        self.btn_next = QtGui.QPushButton('Next')
        self.btn_next.setIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_MediaSeekForward))
        self.btn_next.clicked.connect(self.nextStep)
        
        self.initSession()

        self.stack = QtGui.QStackedWidget()
        #BUILD LAYOUT
        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.stack)
        btnlayout = QtGui.QHBoxLayout()
        btnlayout.addWidget(start)        
        btnlayout.addWidget(self.btn_previous)        
        btnlayout.addWidget(self.btn_next)
        layout.addLayout(btnlayout)
        # BUILD STACK
        for step in content:
            w = QtGui.QWidget()
            l = QtGui.QVBoxLayout()
            w.setLayout(l)
            edit = QtGui.QTextEdit()
            edit.setReadOnly(True)
            edit.setHtml(step.pop('description'))
            l.addWidget(QtGui.QLabel(step.pop('name')))
            l.addWidget(edit)
            self.stack.addWidget(w)
            w.position = step

        self._initCurrentWidget()
        self.activate()
         
 
    def unpackFile(self, path):
        '''
        unpack [path].pyz file to 
        path should be PYZ file with the following content:
        
        =============   =============================================
        File            Description
        =============   =============================================
        tutorial.txt    stores widget positions and tutorial texts
        session.pyz     the initial session from where the tutorial 
                        starts [optional]
                        if this file is not given the tutorial starts 
                        with a new session
        end.pyz         TODO: the final state of the tutorial 
        =============   =============================================
        '''

        tmp_dir = PathStr(tempfile.mkdtemp(
                    'tutorial_%s' %path.basename().split('.')[0]))
        #extract the zip temporally
        ZipFile(path,'r').extractall(path=tmp_dir)

        tut_file = tmp_dir.join('tutorial.txt')
        if not tut_file.exists():
            raise IOError("'tutorial.txt' doesn't exist within the tutorial-file '%s'" %path)
        
        with open(tut_file,'r') as f:
            content = eval(f.read())

        sessionFile = tmp_dir.join('session.pyz')
        #resultFile = self.tmp_dir.join('end.pyz')
        return sessionFile, content

 
 
    def _initCurrentWidget(self):
        '''
        get current tutorial step and grab its widget
        '''        
        e = self.stack.currentWidget()
        self.getWidgetFromPosition(e.position)


    def restart(self):
        '''
        restart the tutorial
        '''
        self.deactivate()
        self.initSession()
        self.stack.setCurrentIndex(0)  
        self._initCurrentWidget()
        self.activate()
        self.btn_previous.setEnabled(False)
        self.btn_next.setEnabled(True)


    def previousStep(self):
        '''
        go one step back in the tutorial
        '''
        i = self.stack.currentIndex()
        if i > 0:
            self.deactivate() #...old
            i -= 1
            self.stack.setCurrentIndex(i)
            self._initCurrentWidget()
            self.activate() #...new
            if i == 0:
                self.btn_previous.setEnabled(False)
            else:
                self.btn_previous.setEnabled(True)
            self.btn_next.setEnabled(True)


    def nextStep(self):
        '''
        go to the next tutorial step
        '''
        i = self.stack.currentIndex()
        if i < self.stack.count()-1:
            self.deactivate() #...old
            i+=1
            self.stack.setCurrentIndex(i)
            self._initCurrentWidget()
            self.activate() #...new
            if i == self.stack.count() - 1:
                self.btn_next.setEnabled(False)
            else:
                self.btn_next.setEnabled(True)
            self.btn_previous.setEnabled(True)
    
    
    def closeEvent(self, evt):
        self.deactivate()
        evt.accept()


    

if __name__ == '__main__':
    import doctest
    doctest.testmod()

            