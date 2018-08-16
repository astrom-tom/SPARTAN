'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
##### Configuration frame of
#####         the TUI
#####
#####
############################
@License: GPLv3.0 - see LICENCE.txt
'''

####Python General library
import multiprocessing
##########################

###Third party###
import npyscreen
################

try:
    import getpass
except:
    pass

class config_win:
    """
    This class manages the first section of the TUI: the project configuration

    Attributes:
        self.PName      Project Name
        self.AName      Author Name
        self.PDir       Project Directory
        #self.Date       Date of the Project Creation
        self.Nnode      Number of node in which SpARTAN will run
        self.NCPU       Number of CPUs  in each node "   "   "   "   "   "
        self.Pcat       Data catalog
        self.UsePhot    Use of photonetry during the fit
        self.UseSpec    Use of the Spectroscopy during the fit
        self.NSpec      Number of spectra per object
    """

    def __init__(self, Log, x, y, CONF):
        """
        Class constructor creating the form and populating it with widgets

        Parameters:
        ----------
        CONF:  A dictionnary containing the information of each widget
               It can be empty or coming from an already defined
               Project
               Format={Project Name, Author,Project directory, Date,\
                       Number of nodes, Number of CPU,Usespec, Usephot}
               Types={str,str,str,date,str,str,int,int}

        Log:   SPARTAN LOGO to be drawn at the top of the form

        x,y:   size of the front page of the TUI. The nez page descibed here
               is drawn on the same size.

        Returns:
        -------

        """

        ###USER NAME, if not specified, try to find the name on the system
        if CONF['AName'] != '':
            Author = CONF['AName']
        else:
            try:
                Author = getpass.getuser()

            except:
                Author = ''


        ####CPUs, if not precised, find on the system and set NCPU=totCPU/2
        if CONF['NCPU'] != '':
            CPUS = CONF['NCPU']
        else:
            try:
                CPUS = str(int(multiprocessing.cpu_count()/2))
            except:
                CPUS = ''

        ###Initialize the Form
        self.C = npyscreen.Form(name="SPARTAN general configuration", color='STANDOUT')

        ###Write the Logo
        for i in Log:
            self.C.add(npyscreen.FixedText, value=i, \
                    relx=int((x-len(i))/2), editable=False, color='CURSOR')

        ###Make the 2 boxes (this is just to make the forn fancier :) )
        n = 9  ###the terminal row where we start to draw the boxes
        self.C.add(npyscreen.BoxBasic, name='Project information', rely=9,\
                 max_width=int(x/2)-1, editable=False, color='DANGER')

        self.C.add(npyscreen.BoxBasic, name='Data Initialization',\
                relx=int(x/2)+1, rely=9, editable=False, color='DANGER')

        ### Make the widgets
        n = 11 ###The terminal row where we start to draw the widgets
        c = 4
        PName = self.C.add(npyscreen.TitleText, name="Project Name:",\
                 value=CONF['PName'], relx=c, rely=n, max_width=30, max_heigth=1, labelColor='CAUTION')

        AName = self.C.add(npyscreen.TitleText, name="Author(*):",\
                 relx=c, rely=n+int((y-n)/9), value=Author, max_width=int(x/3), max_heigth=1, labelColor='CAUTION')

        PDir = self.C.add(npyscreen.TitleFilenameCombo, name="Project Directory [Enter]:",\
                 value=CONF['PDir'], relx=c, rely=n+2*int((y-n)/9), \
                 max_width=int(x/2.5), labelColor='CAUTION')

        Pcat = self.C.add(npyscreen.TitleFilenameCombo, name="Data catalog [Enter]:",\
                 value=CONF['PCat'], relx=c, rely=n+5*int((y-n)/9), \
                 max_width=int(x/2.5), labelColor='CAUTION')

        NCPU = self.C.add(npyscreen.TitleText, name="# CPU:", relx=c, rely=n+7*int((y-n)/9),\
                 value=CPUS, max_width=int(x/3), labelColor='CAUTION')

                ##second column
        if CONF['UseSpec'].lower() == 'yes':
            USESPEC = 1
        elif CONF['UseSpec'].lower() == 'no':
            USESPEC = 0
        else:
            USESPEC = 0

        if CONF['UsePhot'].lower() == 'yes':
            USEPHOT = 1
        elif CONF['UsePhot'].lower() == 'no':
            USEPHOT = 0
        else:
            USEPHOT = 0

        UseSpec = self.C.add(npyscreen.TitleSelectOne, max_height=3, \
                value=[USESPEC, ], name="Spectroscopy", values=["NO", "YES"], \
                scroll_exit=True, relx=int(x/2)+4, rely=n, \
                max_width=int(x/2.5), labelColor='CAUTION')

        NSpec = self.C.add(npyscreen.TitleText, name="NSpec:", relx=int(x/2)+4,\
                 rely=n+int((y-n)/3), value=CONF['NSpec'], \
                 max_width=int(x/3), labelColor='CAUTION')

        UsePhot = self.C.add(npyscreen.TitleSelectOne, max_height=2, \
                 value=[USEPHOT, ], name="Photometry", values=["NO", "YES"], \
                scroll_exit=True, relx=int(x/2)+4, rely=n+2*int((y-n)/3),\
                max_width=int(x/3), labelColor='CAUTION')

        ### To let the user interact with the screen
        self.C.edit()

        ###Define the attributes of the class
        self.PName = PName.value
        self.AName = AName.value
        self.PDir = PDir.value
        self.NCPU = NCPU.value
        self.PCat = Pcat.value
        self.NSpec = NSpec.value

        if UsePhot.value[0] == 1:
            self.UsePhot = 'Yes'
        elif UsePhot.value[0] == '':
            self.UsePhot = ''
        elif UsePhot.value[0] == 0:
            self.UsePhot = 'No'

        if UseSpec.value[0] == 1:
            self.UseSpec = 'Yes'
        elif UseSpec.value[0] == '':
            self.UseSpec = ''
        elif UseSpec.value[0] == 0:
            self.UseSpec = 'No'
