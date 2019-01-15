'''
############################
#####
##### The Spartan Project
#####         GUI
#####      R. THOMAS
#####        2017
#####
#####       general 
#####    distribution
#####
###########################
@author: R. THOMAS
@year: 2017
@place: UV/ESO
@License: GPL v3.0 (a copy is given at the root directory)
'''

###standard python library
import os
import warnings

###third pary
from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, QComboBox,
        QPushButton, QTabWidget, QSpinBox)
from PyQt5.QtGui import QIcon, QPixmap
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

import numpy

import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor

###Local imports
from .              import Results_extract_results as extract


###ignored warning
warnings.simplefilter(action='ignore', category=matplotlib.mplDeprecation)


######################
myFont=QtGui.QFont()
myFont.setBold(True)
myFont.setPointSize(13)
####################3##

class Tabgen(QTabWidget):
    popOut = QtCore.Signal(QWidget)
    popIn = QtCore.Signal(QWidget)

    def __init__(self, filename, dico, style, parent=None):
        super(Tabgen, self).__init__(parent)

        ####load matplotlib style
        dir_path = os.path.dirname(os.path.realpath(__file__))
        matplotlib.style.use(os.path.join(dir_path,'GUI_styles/plot_style/%s'%style))

        ####attributes
        self.filename = filename 
        self.plot = 'no' 

        ###extract parameter names for the tabs
        self.parameters = extract.ListParameters(self.filename, magabsuse = 'yes')
      
        ##create the tab
        self.tab = QTabWidget()
        self.addTab(self.tab, '')
        self.tabdis()

    def tabdis(self,):
        '''
        Method that creates the distribution in the given tab
        '''

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


        ###extract parameter names for the tabs
        ###X selection
        scrolllist = QLabel('Parameter :', self)
        scrolllist.setFont(myFont)
        grid.addWidget(scrolllist, 2, 0,)
        
        self.X = QComboBox(self) 
        grid.addWidget(self.X, 2, 1, ) 
        for i in range(len(self.parameters)):
            self.X.addItem(self.parameters[i])
        
        ###bin size selection
        binsize = QLabel('Number bins', self)
        binsize.setFont(myFont)
        grid.addWidget(binsize, 2, 2)

        self.sp = QSpinBox(self)
        self.sp.setRange(1,1000)
        self.sp.setValue(50)
        grid.addWidget(self.sp, 2, 3,1, 1)

        ###compute button
        compute = QPushButton('Plot!')
        grid.addWidget(compute, 3, 0, 1, 4)
        compute.clicked.connect(self.plotdis)

        ############## The added part: #############
        #def onclick(event):
        #    cursor.onmove(event)
        #    cursor2.onmove(event)
        ############################################

        #### window with plots
        self.figure = Figure()
        self.win = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.win, self)
        self.win.draw()
        grid.addWidget(self.toolbar, 4, 0, 1, 4)
        grid.addWidget(self.win, 5, 0, 2, 4)

        #cursor = Cursor(a2, useblit=False, color='red', linewidth=2 )
        #cursor2 = Cursor(a1, useblit=False, color='red', linewidth=2 )
        #self.win.mpl_connect('button_press_event', onclick)

        self.tab.setLayout(grid)
        

    def plotdis(self,):
        '''
        This method create the plot inside the window when the
        button is pressed
        '''
        #retrieve X
        Xid = self.X.currentText()
        typ = Xid.split('_')
        ###extract the data distribution
        if Xid in ['Redshift', 'Npoints']:
            Xlist = extract.distribution(Xid, 'Observable', self.filename)
        elif Xid in ['Bestchi2']:
            Xlist = extract.distribution(Xid, 'Template', self.filename)
        elif typ[-1] == 'PDF':
            Xlist = extract.distribution(Xid[:-4], 'Parameters_PDF', self.filename) 
        elif typ[-1] == 'BF':
            Xlist = extract.distribution(Xid[:-3], 'Parameters_BF', self.filename)
        elif typ[-1] == 'ABS':
            Xlist = extract.distribution(typ[0], 'Mag_abs', self.filename)

        ###create the binning
        binning = numpy.linspace(min(Xlist), max(Xlist), self.sp.value())

        

        ###and make the plot
        if self.plot == 'no':
            self.a1 = self.figure.add_subplot(111)
            self.a1.set_ylabel('N')
            self.a1.set_xlabel('%s'%Xid)
            self.a1.hist(Xlist, bins = binning, histtype = 'step', lw=1)
            self.a1.minorticks_on()
            self.win.draw()
            self.plot = 'ok'
             
        else:
            self.a1.clear()
            self.a1 = self.figure.add_subplot(111)
            self.a1.set_ylabel('N')
            self.a1.set_xlabel('%s'%Xid)
            self.a1.hist(Xlist, bins = binning, histtype = 'step', lw=1)
            self.a1.minorticks_on()
            self.win.draw()
            self.plot = 'ok'
        self.figure.tight_layout()
