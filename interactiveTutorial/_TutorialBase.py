from PyQt4 import QtGui, QtCore

MyBorderRole = QtCore.Qt.UserRole + 1



class _BorderItemDelegate(QtGui.QStyledItemDelegate):
    '''
    An item delegate for QTreeWidget allowing to draw a border around it's
    QTreeWidgetItems
    '''
    
    def __init__(self, parent, borderRole):
        super(_BorderItemDelegate, self).__init__(parent)
        self.borderRole = borderRole


    def sizeHint(self, option, index):        
        size = super(_BorderItemDelegate, self).sizeHint(option, index)
        pen = index.data(self.borderRole).toPyObject()
        if pen is not None:        
            # Make some room for the border
            # When width is 0, it is a cosmetic pen which
            # will be 1 pixel anyways, so set it to 1
            width = max(pen.width(), 1)            
            size = size + QtCore.QSize(2 * width, 2 * width)
        return size


    def paint(self, painter, option, index):
        pen = index.data(self.borderRole).toPyObject()
        # copy the rect for later...
        rect = QtCore.QRect(option.rect)
        if pen is not None:
            width = max(pen.width(), 1)
            # ...and remove the extra room we added in sizeHint...
            option.rect.adjust(width, width, -width, -width)      
        # ...before painting with the base class method...
        super(_BorderItemDelegate, self).paint(painter, option, index)
        # ...then paint the borders
        if pen is not None:
            painter.save()  
            # The pen is drawn centered on the rectangle lines 
            # with pen.width()/2 width on each side of these lines.
            # So, rather than shifting the drawing of pen.width()/2
            # we double the pen width and clip the part that would 
            # go outside the rect.
            painter.setClipRect(rect, QtCore.Qt.ReplaceClip);          
            pen.setWidth(2 * width)
            painter.setPen(pen)
            painter.drawRect(rect)     
            painter.restore()



class TutorialBase(object):
    '''
    base class for _TutorialStep and RunTutorial
    '''

    def __init__(self):
        self.chosenWidget = None
        self.chosenItem = None
        self.chosenItem_column = 0


    def activate(self):
        '''
        draw red border around QWidget or QTreeWidgetItem
        '''
        widget = self.chosenWidget
        if widget:
            #QTREEWIDGET
            if isinstance(widget, QtGui.QTreeWidget):
                #we can just use setStylesheet for items in QTreeWidget, but we can
                #do the following to draw a red border:
                if not hasattr(widget, '_origItemDelegate'):
                    #setup TreeWidget to draw borders around its items 
                        #backup old:
                    widget._origItemDelegate = widget.itemDelegate()
                        #set new:
                    widget.setItemDelegate(_BorderItemDelegate(widget, MyBorderRole))
                #setup treeWidgetItem:
                if not self.chosenItem:
                    self.chosenItem = widget.currentItem()
                if self.chosenItem:
                    pen = QtGui.QPen(QtCore.Qt.red)
                    pen.setWidth(2)
                    self.chosenItem.setData(self.chosenItem_column, MyBorderRole, pen)
            #ALL OTHER WIDGETS
            else:
                if not hasattr(widget, '_lastStylesheet'):
                    widget._lastStylesheet = widget.styleSheet()
                widget.setStyleSheet('%s {%s}' %(widget.__class__.__name__,'border: 2px solid red;'))


    def deactivate(self):
        '''
        reset border
        '''
        widget = self.chosenWidget
        if widget:
            #QTREEWIDGET
            if isinstance(widget, QtGui.QTreeWidget):
                #reset QTreeWidget:
                if hasattr(widget, '_origItemDelegate'):
                    widget.setItemDelegate(widget._origItemDelegate)
                    del widget._origItemDelegate
                #reset item:
                if self.chosenItem:
                    self.chosenItem.setData(0, MyBorderRole, None)
            #ALL OTHER WIDGETS
            else:
                try:
                    if hasattr(widget, '_lastStylesheet'):
                        widget.setStyleSheet(widget._lastStylesheet)    
                except RuntimeError:
                    pass #wrapped C/C++ object of type ### has been deleted


    def getWidgetFromPosition(self, position):
        '''
        get a QWidget/QTreeWidgetItem from its position
        store the result under 
        ... self.chosenWidget
        ... self.chosenItem
        ... self.chosenItem_column
        '''
        indices = position.get('childPosFromMainWindow')
        if indices:
            #FIND WIDGET
            wintitle = indices[0]
            widgetclsname = indices[1]
            foundwidget = False
            for widget in QtGui.QApplication.instance().topLevelWidgets():
                #1. try to find the right window through the window title
                if widget.windowTitle() == wintitle:
                    foundwidget = True
                    break
            if not foundwidget:
                #2. if 1. doesn't work: find window through it's class name  
                for widget in QtGui.QApplication.instance().topLevelWidgets():
                    if widget.__class__.__name__ == widgetclsname:
                        break

            for clsname, layoutpos in indices[2:]:
                found = False
                n = 0
                for ch in widget.children():
                    #1. find widgets of the same class name
                    if ch.__class__.__name__ == clsname:
                        layout = widget.layout
                        if callable(layout):
                            layout = layout()
                        #2. now check whether the position within the parent layout is the same
                        if (ch.isVisible() and 
                        (layoutpos == None or layout.indexOf(ch) == layoutpos) 
                        or n == layoutpos):
                            widget = ch
                            found = True
                            break
                        n += 1

                if not found:
                    print "couldn't load widget. Did you follow all previous steps?"
                    self.chosenWidget = None
                    return

            #QTREEWIDGET
            if isinstance(widget, QtGui.QTreeWidget):
                #get item within the tree
                (row_indices, self.chosenItem_column) = position['treeIndices']
                item = widget.topLevelItem(row_indices[0])
                for i in row_indices[1:]:
                    item = item.child(i)
                    # make item visible in case it's hidden:
                    widget.expandItem(item)
                self.chosenItem = item
            self.chosenWidget = widget   
        else:
            self.chosenWidget = None