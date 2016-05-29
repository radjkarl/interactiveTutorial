from PyQt4 import QtGui


class TestProgram(QtGui.QMainWindow):
    '''
    A minimal program for testing the interactiveTutorial
    including 
    ... buttons, 
    ... some text to change, 
    ... a method for saving and opening a session
    '''

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.resize(500,600)
        self.setWindowTitle('Test program')

        w = QtGui.QWidget()
        self.setCentralWidget(w)
        
        layout = QtGui.QGridLayout()
        w.setLayout(layout)

        btn_save = QtGui.QPushButton('save')
        btn_save.clicked.connect(lambda: self.save())

        btn_open = QtGui.QPushButton('open')
        btn_open.clicked.connect(lambda: self.open())

        self.ckb_1 = QtGui.QCheckBox('one')
        self.ckb_2 = QtGui.QCheckBox('two')
        self.le_1 = QtGui.QLineEdit('text1')
        self.le_2 = QtGui.QLineEdit('text2')
        #QTREEWIDGET
        self.tree = QtGui.QTreeWidget()
        self.tree.setColumnCount(2)
        item0 =  QtGui.QTreeWidgetItem(self.tree)
        item0.setText(0, "foo")
        self.tree.setItemExpanded (item0, True)
        item1 =  QtGui.QTreeWidgetItem(item0)
        item1.setText(0, "lineedit")
        self.le_3 =  QtGui.QLineEdit('tree')
        self.tree.setItemWidget (item1, 1, self.le_3)

        layout.addWidget(btn_save)
        layout.addWidget(btn_open)        
        layout.addWidget(self.ckb_1)
        layout.addWidget(self.ckb_2)
        layout.addWidget(self.le_1)
        layout.addWidget(self.le_2)
        layout.addWidget(self.tree)
        
        
    def save(self, fname=None):
        if fname is None:
            fname = QtGui.QFileDialog.getSaveFileName()
        if fname:
            l = {}
            l['ckb_1'] = self.ckb_1.isChecked()
            l['ckb_2'] = self.ckb_2.isChecked()
            l['le_1'] = str(self.le_1.text())            
            l['le_2'] = str(self.le_2.text())            
            l['le_3'] = str(self.le_3.text())            
            
            with open(fname, 'w') as f:
                f.write(str(l))


    def open(self, fname=None):
        if fname is None:
            fname = QtGui.QFileDialog.getOpenFileName()
        if fname:    
            with open(fname, 'r') as f:
                l = eval(f.read())
                self.ckb_1.setChecked(l['ckb_1'])
                self.ckb_2.setChecked(l['ckb_1'])
                self.le_1.setText(l['le_1'])
                self.le_2.setText(l['le_2'])
                self.le_3.setText(l['le_3'])
     

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication([])
    win = TestProgram()
    win.show()
    sys.exit(app.exec_())

        
        