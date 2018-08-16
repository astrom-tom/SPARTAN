'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
#####   File of the cosmo
#####       page TUI
#####
###########################
@License: GPL licence - see LICENCE.txt
'''
####Third party##
import npyscreen
#################

class Cosmo_win:
    """
    This class manages the cosmological section of the TUI: the project configuration

    Attributes:
       self.HO      Hubble constant
       self.OM      Matter density parameter
       self.OL      Dark Energy Density parameter
       Self.UseCo   Use COSMO [YES/NO]

    """
    def __init__(self, Log, x, y, COSMO):

        """
        Class constructor creating the form and populating it with widgets
        Parameters:
        ----------
        COSMO: A dictionnary containing the information of each widget
               It can be empty or coming from an already defined Project
               Format={Ho, Omega_m, Omega_L,UseCosmo}
               Types={str,str,str,int}

        Log:   SPARTAN LOGO to be drawn at the top of the form

        x,y:   size of the front page of the TUI. The nez page descibed here
               is drawn on the same size.

        Returns:
        -------
        """
        ##Initialize form and write logo
        self.Co = npyscreen.Form(name="SPARTAN Cosmological model", color='STANDOUT')
        ##Write Logo
        for i in Log:
            self.Co.add(npyscreen.FixedText, value=i, relx=int((x-len(i))/2), editable=False)

        ####Make the boxes
        n = 9 ##Terminal row where we draw the boxes
        self.Co.add(npyscreen.BoxBasic, name='Cosmological model', rely=n, \
                max_width=int(x/2)-1, editable=False, color='DANGER')
        self.Co.add(npyscreen.BoxBasic, name='Additional informations',\
                 relx=int(x/2)+1, rely=9, editable=False, color='DANGER')

        ###Create the widgets
        n = 11 ## Terminal row where we start to draw the widgets
        HO = self.Co.add(npyscreen.TitleText, name='Ho[km/s/Mpc]=', relx=8,\
                 rely=n, max_width=int(x/3), value=COSMO['Ho'], labelColor='CAUTION')

        OM = self.Co.add(npyscreen.TitleText, name='Omega_m=', relx=8,\
                 rely=n+int((y-n)/4), max_width=int(x/3), value=COSMO['Omega_m'],\
                 labelColor='CAUTION')

        OL = self.Co.add(npyscreen.TitleText, name='Omega_L=', relx=8\
                ,rely=n+2*int((y-n)/4), max_width=int(x/3), value=COSMO['Omega_L'],\
                labelColor='CAUTION')

        if COSMO['UseCo'].lower() == 'yes':
            USE = 1
        elif COSMO['UseCo'].lower() == 'no':
            USE = 0
        else:
            USE = 1

        UseCO = self.Co.add(npyscreen.TitleSelectOne, name="Use Cosmology",\
                values=["NO", "YES"], value=[USE], scroll_exit=True, relx=8,\
                 rely=n+3*int((y-n)/4), max_height=int(2), max_width=int(x/3),labelColor='CAUTION')

        v = 'During the fit, 2 options are\navailable. \nYou can use cosmology (default).\n\
At a given redshift, the age of \nthe templates will be limited by\nthe age of the Universe at that\nredshift. If you do \
not use it,\nthe fit will considered all the\navailable age of the librairy.\n\n\nL-CDM: Ho=70; OL=0.73; Om=0.27\nE-De-S:Ho=70; OL=0.00; Om=1.0'

        self.Co.add(npyscreen.MultiLineEdit, value=v, relx=int(x/2)+2, rely=11,\
                 max_width=int(x/2.5), editable=False)

        ###To let the user interact with the screen
        self.Co.edit()

        ###Define the attributes of the class
        self.Ho = HO.value
        self.Omega_m = OM.value
        self.Omega_L = OL.value
        if UseCO.value[0] == 1:
            self.UseCo = 'Yes'
        if UseCO.value[0] == 0:
            self.UseCo = 'No'
