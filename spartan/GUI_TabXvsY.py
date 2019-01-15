'''
############################
#####
##### The Spartan Project
#####         GUI
#####      R. THOMAS
#####        2017
#####
#####        XvsY
#####        
#####
###########################
@author: R. THOMAS
@year: 2017
@place: UV/ESO
@License: GPL v3.0 (a copy is given at the root directory)
'''


###python standard library
import warnings
import os


###third party
import numpy
from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, QComboBox,
        QPushButton, QTabWidget, QSpinBox, QTableWidget, QHeaderView, QTableWidgetItem)
from PyQt5.QtGui import QIcon, QPixmap, QStandardItemModel
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
import matplotlib.gridspec as gridspec
#matplotlib.use('Qt5Agg')


##ignored warnings
warnings.simplefilter(action='ignore', category=matplotlib.mplDeprecation)

###Local imports
from .           import Results_extract_results as extract

myFont=QtGui.QFont()
myFont.setBold(True)
myFont.setPointSize(13)

class TabXvsY(QTabWidget):
    popOut = QtCore.Signal(QWidget)
    popIn = QtCore.Signal(QWidget)

    def __init__(self, filename, dico, style, parent=None):
        super(TabXvsY, self).__init__(parent)

        self.filename = filename
        self.dico = dico
        self.style = style

        ####load matplotlib style
        dir_path = os.path.dirname(os.path.realpath(__file__))
        matplotlib.style.use(os.path.join(dir_path,'GUI_styles/plot_style/%s'%style))

        #####extract parameter names for the tabs
        self.parameters = extract.ListParameters(self.filename, magabsuse = 'yes')

        ##create the tab
        self.tab = QTabWidget()
        self.addTab(self.tab, '')
        self.table()

       
    def table(self):
        '''
        Method that creates the distribution in the given tab
        '''
        self.plot = 'no' 
        ### Draw the grid
        grid = QGridLayout()

        ####Display pop in / pop out button
        popOutButton = QPushButton('Pop Out')
        popOutButton.clicked.connect(lambda: self.popOut.emit(self))
        self.popOut.emit(self)
        popInButton = QPushButton('Pop In')
        popInButton.clicked.connect(lambda: self.popIn.emit(self))
        grid.addWidget(popOutButton, 0 , 0, 1, 2)
        grid.addWidget(popInButton, 0, 2, 1, 2)

        
        ###X selection
        scrolllist = QLabel('Select X-axis:', self)
        grid.addWidget(scrolllist, 2, 0,)

        self.X = QComboBox(self) 
        grid.addWidget(self.X, 2, 1, ) 
        for i in range(len(self.parameters)):
            self.X.addItem(self.parameters[i])

        ###Y selection
        scrolllist = QLabel('Select Y-axis:', self)
        grid.addWidget(scrolllist, 2, 2,)

        self.Y = QComboBox(self) 
        grid.addWidget(self.Y, 2, 3, ) 
        for i in range(len(self.parameters)):
            self.Y.addItem(self.parameters[i])

        
        ###compute button
        compute = QPushButton('Plot!')
        grid.addWidget(compute, 3, 0, 1, 4)
        compute.clicked.connect(self.plotxy)


        #### window with plots
        self.figure = Figure()
        self.figure.subplots_adjust(hspace = 0.8, wspace = 0.3, top = 0.95, left = 0.13, bottom=0.15, right=0.95)
        self.win = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.win, self)
        self.win.draw()
        grid.addWidget(self.toolbar, 4, 0, 1, 4)
        grid.addWidget(self.win, 5, 0, 2, 4)

        self.tab.setLayout(grid)
    
        

    def plotxy(self,):
        '''
        This method create the plot inside the window when the
        button is pressed
        '''
        
        #retrieve X
        Xid = self.X.currentText()
        
        #retrieve Y
        Yid = self.Y.currentText()
        

        ###extract the data
        Xlist, Ylist = extract.extract_couple(self.filename, Xid, Yid)

        
        ###and make the plot
        if self.plot == 'no':
            self.a1 = self.figure.add_subplot(111)
            self.a1.set_ylabel(Yid)
            self.a1.set_xlabel(Xid)
            self.a1.scatter(Xlist, Ylist, facecolor='none', edgecolor='r', lw=0.4)
            self.win.draw()
            self.plot = 'ok'

        else:
            self.a1.clear()
            self.a1 = self.figure.add_subplot(111)
            self.a1.set_ylabel(Yid)
            self.a1.set_xlabel(Xid)
            self.a1.scatter(Xlist, Ylist, facecolor='none', edgecolor='r', lw=0.4)
            self.win.draw()
            self.plot = 'ok'

