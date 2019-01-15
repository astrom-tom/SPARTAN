'''
############################
#####
##### The Spartan Project
#####         GUI
#####      R. THOMAS
#####        2017
#####
#####        Tabfit
#####        
#####
###########################
@author: R. THOMAS
@year: 2017-2018
@place: UV/ESO
@License: GPL v3.0 (a copy is given at the root directory)
'''

###Standard Library
import os
import warnings


###python third party imports
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

###Local imports
from .          import Results_extract_results as extract


###ignored warnings
warnings.simplefilter(action='ignore', category=matplotlib.mplDeprecation)

##pyqt5 font
myFont=QtGui.QFont()
myFont.setPointSize(13)

class Tabfit(QTabWidget):
    popOut = QtCore.Signal(QWidget)
    popIn = QtCore.Signal(QWidget)

    def __init__(self, filename, ident, CONF, style, parent=None):
        super(Tabfit, self).__init__(parent)


        ####load matplotlib style
        dir_path = os.path.dirname(os.path.realpath(__file__))
        matplotlib.style.use(os.path.join(dir_path,'GUI_styles/plot_style/%s'%style))

        self.filename = filename
        self.ident = ident
        self.CONF = CONF

        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.addTab(self.tab1,"Display FIT")
        self.addTab(self.tab2,"Display PDF")
        self.tabfit()
        self.tab2UI(self.tab2, self.ident, self.filename)

    def tabfit(self):
        
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

        #### window with plots
        self.figure = Figure()
        self.figure.subplots_adjust(hspace = 0, right=0.95, top=0.94, left=0.15)
        self.win = FigureCanvas(self.figure)
        self.win.draw()
        grid.addWidget(self.win, 3, 0, 2, 4)
        self.toolbar = NavigationToolbar(self.win, self)
        grid.addWidget(self.toolbar, 2, 0, 1, 4)
        
        gs = gridspec.GridSpec(1, 1)
        self.fitplot = self.figure.add_subplot(gs[:1,:])

        ####customizing
        self.fitplot.minorticks_on()
        toplot = extract.extract_fit(self.CONF, self.ident, self.filename)
        
        if self.CONF.CONF['UsePhot'].lower() == 'yes' and self.CONF.CONF['UseSpec'].lower() == 'no':
            self.photplot(toplot)

        if self.CONF.CONF['UsePhot'].lower() == 'no' and self.CONF.CONF['UseSpec'].lower() == 'yes':
            self.specplot(toplot)

        if self.CONF.CONF['UsePhot'].lower() == 'yes' and self.CONF.CONF['UseSpec'].lower() == 'yes':
            print('Comb')

        self.tab1.setLayout(grid)

    def specplot(self, toplot):

        ###unpack
        BFtemp_wave, BFtemp, BF_regrid, SPECS = toplot

        ##and plot fit
        self.fitplot.clear()


        mins = []
        maxs = []
        for i in list(SPECS.keys()):
            if i == '1':
                self.fitplot.plot(SPECS[i][0], SPECS[i][1], color='deepskyblue', \
                        lw=0.3, label='Observed')
                self.fitplot.fill_between(SPECS[i][0], 0, SPECS[i][1], color='0.3', lw=0.0)
                self.fitplot.plot(SPECS[i][0], SPECS[i][2], color='Orange', lw=0.3, label='Error')
            else:
                self.fitplot.plot(SPECS[i][0], SPECS[i][1], color='g', lw=0.8)
                self.fitplot.plot(SPECS[i][0], SPECS[i][2], color='g', lw=0.8)

            mins.append(min(SPECS[i][0]))
            maxs.append(max(SPECS[i][0]))

        self.fitplot.plot(BFtemp_wave, BFtemp, color='r', label='Best fit template')

        self.fitplot.tick_params(labelbottom = 'off')
        self.fitplot.axhline(0, lw=0.5, ls='--', color='yellow')
        self.fitplot.legend(ncol = 3)
        self.fitplot.set_xlim(min(mins)-1000, max(maxs)+1000)
        self.fitplot.set_ylabel('Flux Density')
        self.fitplot.set_title('Galaxy #%s'%self.ident, fontsize=4)

    def photplot(self, toplot):

        ###unpack
        wavelength, flux, fluxerr, obsmag, BFtemp, BFtemp_wave, Bestfit_flux, Bestfit_mag = toplot

        ##and plot fit
        self.fitplot.clear()
        self.fitplot.plot(BFtemp_wave, BFtemp, color='r', label='Best fit template', zorder=0)
        self.fitplot.scatter(wavelength, Bestfit_flux, s = 20, color = 'lime', \
                label='Best fit magnitudes', zorder=1)

        self.fitplot.scatter(wavelength, flux, marker = '*', s=20, \
                facecolor = 'none', edgecolor='fuchsia', lw=0.5, zorder=2,\
                label='Observed Magnitude')

        self.fitplot.errorbar(wavelength, flux, yerr = [fluxerr,fluxerr],\
                fmt='none', marker = '*', lw=1. ,color='blue',label = 'Observed error', \
                zorder=3, capsize=5, elinewidth=0.5,)

        self.fitplot.tick_params(labelbottom = 'off')
        self.fitplot.axhline(0, lw=0.5, ls='--', color='b')
        self.fitplot.legend()
        ##axis
        self.fitplot.set_ylim(min(flux) - min(flux)*1.5, 1.5*max(flux))
        self.fitplot.set_ylabel('Flux Density')
        self.fitplot.set_title('Galaxy #%s'%self.ident, fontsize=12)



    def tab2UI(self, tab2, ident, filename):
        ####################
        grid = QGridLayout()


        ###extract parameter names for the tabs
        parameters = extract.ListParameters(self.filename, magabsuse = 'no')

        ##split BF / PDF
        BF = []
        PDF = []
        for i in parameters:
            s = i.split('_')
            if len(s) >= 2:
                if s[-1] == 'BF': 
                    BF.append(i[:-3])
                if s[-1] == 'PDF':
                    PDF.append(i[:-4])


        BFp = extract.extract_full_obj(self.filename, self.ident, ['Redshift', 'Npoints', 'Bestchi2']+BF, 'Parameters_BF', 'BF')
        PDFp = extract.extract_full_obj(self.filename, self.ident, ['Redshift', 'Npoints', 'Bestchi2']+PDF, 'Parameters_PDF', 'PDF') 

        ####table for parameters
        tableWidget = QTableWidget()
        tableWidget.setRowCount(2)
        listp = ['Redshift', 'Npoints', 'bestChi2']+BF 
        tableWidget.setColumnCount(len(listp))

        for i in range(len(listp)):
            tableWidget.setItem(0, i, QTableWidgetItem(str(BFp[i])))
            tableWidget.setItem(1, i, QTableWidgetItem(str(PDFp[i])))
        
        tableWidget.setHorizontalHeaderLabels(listp)
        tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        header = tableWidget.horizontalHeader()
        header.setStretchLastSection(True)
        tableWidget.setVerticalHeaderLabels(['BF', 'PDF'])
        tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        header = tableWidget.verticalHeader()
        header.setStretchLastSection(True)
        grid.addWidget(tableWidget, 0, 0, 3, 4)

        #### window with plots

        ###set  number of rows and column
        Rows = int(len(PDF)/2) + 1
        Column = 2

        self.figure = Figure()
        self.win = FigureCanvas(self.figure)
        self.figure.subplots_adjust(hspace = 1.8, wspace = 1.3)
        self.win.draw()
        grid.addWidget(self.win, 4, 0, 2, 4)
        self.toolbar = NavigationToolbar(self.win, self)
        grid.addWidget(self.toolbar, 3, 0, 1, 4)
        
        for i in range(len(PDF)):
            self.pdfcdf = self.figure.add_subplot(Rows, Column, i+1)
            gr, PDFfull, CDFfull = extract.extract_PDF_CDF(self.filename, self.ident, PDF[i])
            self.pdfcdf.plot(gr, PDFfull/max(PDFfull), color='fuchsia')
            self.pdfcdf.fill_between(gr,0, PDFfull/max(PDFfull), color='fuchsia', alpha=0.2, lw=0.2 )
            self.pdfcdf.plot(gr, CDFfull, color='lime')
            ##customize
            #self.pdfcdf.set_xlabel(PDF[i])
            #self.pdfcdf.set_ylabel('P')
            self.pdfcdf.text(min(gr), 0.5, PDF[i], fontsize=5)
        
        self.figure.tight_layout()
        tab2.setLayout(grid)


