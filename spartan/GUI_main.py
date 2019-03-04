'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####      2016-2019
#####
#####   COde for the GUI
#####
###########################
@License: GPL - see LICENCE.txt
'''
####Public General Libraries
import os
import sys
from functools import partial


####Third party
import  numpy
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QLabel, QComboBox,
        QPushButton, QTabWidget, QShortcut, QMenu, QToolBar, QAction)
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui

####local imports
from .              import GUI_Logo as logos
from .              import messages as MTU
from .GUI_Tabgen    import Tabgen 
from .GUI_Tabfit    import Tabfit
from .GUI_TabXvsY   import TabXvsY
from .              import Results_extract_results as data


#####################FONT QT4, size and bold
myFont=QtGui.QFont()
myFont.setBold(True)
myFont.setPointSize(13)
######################

class Main_window(QWidget):
    
    def __init__(self, resfile, CONF):
        super().__init__() 
        self.resfile = resfile
        self.dico = data.ListID_dico(self.resfile)
        self.CONF = CONF
        self.index = 0
        self.indexmax = 0
        self.initUI() 
        self.setWindowTitle('SPARTAN GUI: %s'%os.path.basename(self.resfile))

    def initUI(self):
             
        ### 0 we create the grid
        grid = QGridLayout()
        self.setLayout(grid)

        #### 1 -LOGO
        label = QLabel(self)
        pixmap = QPixmap(logos.Logo())
        pixmap4 = pixmap.scaled(800, 800, QtCore.Qt.KeepAspectRatio) 
        label.setToolTip('Useful keyboard shortcuts:\n'+\
                'f --> show fit\n' + 'n --> show next fit\n' + 'b --> show previous fit\n' + \
                'Ctrl + w --> close current tab\n' + 'Ctrl + Page Up --> see previous tab\n' + \
                'Ctrl + Page Down --> see next tab\n' + 's --> save plotted data to disk')
        label.setScaledContents(True)
        label.setPixmap(pixmap4)
        grid.addWidget(label, 0, 1, 1, 8)


        #### 2 -Individual part
        #### a - Title of the section
        indiv = QLabel('Individual results', self)
        indiv.setAlignment(QtCore.Qt.AlignCenter)
        indiv.setFont(myFont)
        grid.addWidget(indiv, 1, 4, 1, 2)

        #### b - select id label
        scrolllist = QLabel('Select ID:', self)
        grid.addWidget(scrolllist, 2, 1, 1, 2)

        #### c - scrooling list
        self.combo = QComboBox(self)
        grid.addWidget(self.combo, 2, 2, 1, 3)
        self.count = 0
        self.listID = list(self.dico.keys())
        for i in range(len(self.listID)):
            self.combo.addItem(self.listID[i])

        #### d - status
        self.lbl = QLabel(self.listID[self.count], self)        
        self.onActivated(self.listID[0]) #<--- for the opening window
        grid.addWidget(self.lbl, 2, 5, 1, 2)
        self.combo.activated[str].connect(self.onActivated) 

        #### e- show fit panel maker
        self.button = QPushButton("Show Fit")
        self.button.setToolTip('Tab with fitting visualization and parmeter estimations')
        grid.addWidget(self.button, 2, 7, 1, 2)
        self.button.clicked.connect(self.showfit)

        #### f- previous button
        self.previous = QPushButton("Previous")
        self.previous.setToolTip('Go to next ID')
        grid.addWidget(self.previous, 3, 1, 1, 4)
        self.previous.clicked.connect(self.goback)

        #### g- next button
        self.next = QPushButton("Next")
        self.next.setToolTip('Go to next ID')
        grid.addWidget(self.next, 3, 5, 1, 4)
        self.next.clicked.connect(self.gonext)


        ### 3- Global part
        ### a- title of the section 
        globl = QLabel('Global results:')
        globl.setAlignment(QtCore.Qt.AlignCenter)
        globl.setFont(myFont)
        grid.addWidget(globl, 4, 1, 1, 2)

        ### b- show dostribution button
        dist = QPushButton("Show distributions")
        dist.setToolTip('This will open a all the distribution of parameters')
        grid.addWidget(dist, 4, 3, 1, 2)
        dist.clicked.connect(self.general_tab)


        ### c- show distribution button
#        table = QPushButton("Show table of result")
#        table.setToolTip('This will open a new tab with a complete table of the results')
#        grid.addWidget(table, 4, 5, 1, 2)
#       table.clicked.connect(self.table)

        ### d- plt x vs Y
        xvy = QPushButton("X vs Y")
        xvy.setToolTip('This will open a new tab with a plot X vs Y where you can choose X and Y')
        grid.addWidget(xvy, 4, 7, 1, 2)
        xvy.clicked.connect(self.xvsy)

        #### 4a - Style
        scrollstyle = QLabel('Choose Plot Style', self)
        scrollstyle.setFont(myFont)
        grid.addWidget(scrollstyle, 6, 1, 1, 2)


        #### 4b - scrooling list
        self.style = QComboBox(self)
        style_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'GUI_styles/plot_style')


        self.liststyle = os.listdir(style_path)
        for i in self.liststyle:
            if i[-1] != '~':
                self.style.addItem(i)
        grid.addWidget(self.style, 6, 3, 1, 2)

        #### 5 - save data for plotting
        savedata = QPushButton("Save plot data")
        grid.addWidget(savedata, 6, 7, 1, 2)
        savedata.clicked.connect(self.savedata)

        ### 6- space for tabs
        self.tab = QTabWidget()
        grid.addWidget(self.tab, 7, 1, 1, 8)

        ### 7- set keyboard shortcuts
        #Close tab
        self.shortcut = QShortcut(QKeySequence("Ctrl+w"), self)
        self.shortcut.activated.connect(partial(self.closeTab_keyboard, self.index))

        #Close tab
        self.showcurrent = QShortcut(QKeySequence("f"), self)
        self.showcurrent.activated.connect(self.showfit)

        #next fit
        self.shortcut_nextfit = QShortcut(QKeySequence("n"), self)
        self.shortcut_nextfit.activated.connect(self.nextfit)

        #next fit
        self.shortcut_prevfit = QShortcut(QKeySequence("b"), self)
        self.shortcut_prevfit.activated.connect(self.prevfit)



        #next Tab
        self.shortcut_nextTab = QShortcut(QKeySequence("Ctrl+PgDown"), self)
        self.shortcut_nextTab.activated.connect(self.nextTab)

        #next Tab
        self.shortcut_prevTab = QShortcut(QKeySequence("Ctrl+PgUp"), self)
        self.shortcut_prevTab.activated.connect(self.previousTab)

        #save files
        self.shortcut_savefiles = QShortcut(QKeySequence("s"), self)
        self.shortcut_savefiles.activated.connect(self.savedata)


 
        ###icon
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(logos.icon()))
        self.setWindowIcon(icon)    
        self.show()

    def closeTab(self, currentIndex):
        self.tab.removeTab(currentIndex)

    def closeTab_keyboard(self, currentIndex):
        self.tab.removeTab(currentIndex)

    def nextTab(self):
        '''
        Method that allows one to change to the next tab with
        a keyboard shortcut
        '''
        if self.index + 1 >= self.indexmax:
            self.tab.setCurrentIndex(self.index+1)
            self.index = self.indexmax
        else:
            self.tab.setCurrentIndex(self.index+1)
            self.index += 1

    def previousTab(self):
        '''
        Method that allows one to change to the next tab with
        a keyboard shortcut
        ''' 
        self.tab.setCurrentIndex(self.index-1)
        if self.index > 0:
            self.index -= 1


    def nextfit(self):
        '''
        Method that combines the next fir button and show fit button.
        used for keyboard shortcut
        '''
        self.gonext()
        self.showfit()

    def prevfit(self):
        '''
        Method that combines the next fir button and show fit button.
        used for keyboard shortcut
        '''
        self.goback()
        self.showfit()
 
    def showfit(self,):
        self.nametab = 'showfit'
        a = self.tab.count()
        self.createTab(a) 

    def xvsy(self,):
        self.nametab = 'xvsy'
        a = self.tab.count()
        self.createTab(a) 

    def savedata(self):
        '''
        Method that send the data to the save_data function
        parameters:
        -----------
        ident,
                str, id of the galaxy
        Return
        ------
        None
        '''
        obj = str(self.combo.currentText())
        savedata = save_to_disk(self.CONF, obj, self.resfile)
        
    def general_tab(self,):
        self.nametab = 'gen'
        a = self.tab.count()
        self.createTab(a) 

    def createTab(self, a):
        self.tab.setTabsClosable(True)
        self.tab.tabCloseRequested.connect(self.closeTab)

        if self.nametab == 'gen':
            tab = Tabgen(self.resfile, self.dico, str(self.style.currentText()))
            tab.popIn.connect(self.addTab)
            tab.popOut.connect(self.removeTab)
            self.index = self.tab.addTab(tab, 'General properties' ) 
            if self.index > self.indexmax:
                self.indexmax = self.index
            self.tab.setCurrentIndex(self.index)

        if self.nametab == 'showfit':
            ident = str(self.combo.currentText())
            MTU.Info('Show fit for %s, %s/%s'%(ident, self.count+1, len(self.listID)), 'Yes')

            tab = Tabfit(self.resfile, ident, self.CONF, str(self.style.currentText()))
            tab.popIn.connect(self.addTab)
            tab.popOut.connect(self.removeTab)
            self.index = self.tab.addTab(tab, '%s' % ident)
            if self.index > self.indexmax:
                self.indexmax = self.index
 
            self.tab.setCurrentIndex(self.index)
        
        if self.nametab == 'xvsy':
            tab = TabXvsY(self.resfile, self.dico, str(self.style.currentText()))
            tab.popIn.connect(self.addTab)
            tab.popOut.connect(self.removeTab)
            self.index = self.tab.addTab(tab, 'X vs Y' )
            if self.index > self.indexmax:
                self.indexmax = self.index
 
            self.tab.setCurrentIndex(self.index)

 
    def addTab(self, widget):
        if self.tab.indexOf(widget) == -1:
            widget.setWindowFlags(QtCore.Qt.Widget)
            self.tab.addTab(widget, widget.windowTitle())

    def removeTab(self, widget):
        index = self.tab.indexOf(widget)
        if index != -1:
            self.tab.removeTab(index)
            widget.setWindowFlags(QtCore.Qt.Window)
            widget.show()

    def onActivated(self, ident):
        '''
        Method that Updates the fitting status
        it updates the status when a ID is selected in
        the list

        Parameter
        ---------
        ident
                str, ident of the object
        Return
        ------
        None
        '''

        ident = str(self.combo.currentText())
        ind = numpy.where(numpy.array(self.listID) == ident)[0]
        if self.dico[ident] == 'Fitted':
            ##if the object was fitted --> green
            self.lbl.setStyleSheet('color: green')
            self.lbl.setText('Fitted, %s/%s'%(ind+1, len(self.listID)))
            self.lbl.setFont(myFont)
            ###and update the count
            self.count = numpy.where(numpy.array(self.listID) == ident)[0][0]

        else:
            ##if the object was not fitted --> red
            self.lbl.setStyleSheet('color: red')
            self.lbl.setText('NOT Fitted, %s/%s'%(ind+1, len(self.listID)))
            self.lbl.setFont(myFont)
            ###and update the count
            self.count = numpy.where(numpy.array(self.listID) == ident)[0][0]             

    def gonext(self,):
        #Next button method. 
        ####update the count
        if self.count >= len(self.listID)-1:
            self.count = 0
        else:
            self.count += 1

        ###and set the new id in the list
        a = self.combo.findText(self.listID[self.count])
        self.combo.setCurrentIndex(a)
        ###and update the status 
        self.onActivated(self.listID[self.count])

    def goback(self,):
        #Previous button method.
        ###update the count
        if self.count < 0:
            self.count = len(self.listID)-1
        else:
            self.count -= 1
        ####and setr the new id in the list widget
        a = self.combo.findText(self.listID[self.count])
        self.combo.setCurrentIndex(a)
        ### update the status
        self.onActivated(self.listID[self.count])


def start_gui(CONF, resfile):
    '''
    Function that start the gui main window
    Parameter
    --------
    CONF        Configuration of the project 
    resfile     Path to the result file
    '''

    app = QApplication(sys.argv)
    main = Main_window(resfile, CONF)
    main.setFixedSize(730, 1030)
    sys.exit(app.exec_())


def save_to_disk(conf, ident, resfile):
    '''
    Function that saves to the disk the data for plotting
    '''

    toplot = data.extract_fit(conf, ident, resfile)
    if conf.CONF['UsePhot'].lower() == 'yes' and conf.CONF['UseSpec'].lower() == 'no':
        print('phot')

    if conf.CONF['UsePhot'].lower() == 'no' and conf.CONF['UseSpec'].lower() == 'yes':
        ###unpack
        status, BFtemp_wave, BFtemp, BF_regrid, SPECS = toplot
        
        if status == 'Fitted':
            waveall = []
            fluxall = []
            errall = []
            for i in list(SPECS.keys()):
                waveall.append(SPECS[i][0])
                fluxall.append(SPECS[i][1])
                errall.append(SPECS[i][2])
            if len(waveall) != 1:
                waveall = numpy.concatenate(waveall)
                fluxall = numpy.concatenate(waveall)
                errall = numpy.concatenate(waveall)
            else:
                waveall = SPECS['1'][0]
                fluxall = SPECS['1'][1]
                errall = SPECS['1'][2]

            
            ##check if save directory exist
            savedir = os.path.join(conf.CONF['PDir'] , 'save_ascii_fits', ident)
            if not os.path.isdir(savedir):
                os.makedirs(savedir)

            ##save_data
            savedata = os.path.join(savedir, 'data.txt')
            numpy.savetxt(savedata, numpy.array([waveall, fluxall, errall]).T)

            ##save_fit
            savefit = os.path.join(savedir, 'fit_spec_wave.txt')
            numpy.savetxt(savefit, numpy.array([waveall, BF_regrid]).T)
            savefit_orig = os.path.join(savedir, 'fit.txt')
            numpy.savetxt(savefit_orig, numpy.array([BFtemp_wave, BFtemp]).T)

            MTU.Info('Plotting data for %s saved in %s'%(ident, savedir), 'No')

        else:
            MTU.Info('Plotting data not saved for failed fit: obj %s '%(ident), 'No')


    #if conf.CONF['UsePhot'].lower() == 'yes' and conf.CONF['UseSpec'].lower() == 'yes':

