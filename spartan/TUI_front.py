'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####      2016-2018
#####
#####   File of the front
#####       page TUI
#####
###########################
@License: CeCILL-v2 licence - see LICENCE.txt
'''
####Public General Libraries
import os
############################

###Third Party##############
import npyscreen
###########################

#####Local Modules ###############
from .             import messages as TUI_messages
from .config_check import check
from .             import TUI_conf_gen as conf
from .             import TUI_cosmo as cosmo
from .             import TUI_fit as fit
from .             import TUI_phot as phot
from .             import TUI_lib as lib
from .             import TUI_spec as spec
###################################

class Front(npyscreen.NPSApp):
    """
    This class manages the Front frame of the TUI.
    It gives access to the 6 configuration frames of SPARTAN

    Attributes:
    ----------
    self.F          Form of the front page
    self.INPUT_CONF Python object containing all the
                    configuration dictionnary of SPARTAN.
                    Can be from user or from the SPARTAN template
    Returns:
    -------
    Iffit           tell spartan to start the fit after
                    the configuration or not

    CONFIG          Python dictionnary containing all the
                    configuration of SPARTAN

    """

    def __init__(self, INPUT_CONF):
        """
        Class Constructor

        Parameters
        ---------
        INPUT_CONF  input configuration. Can be from the default template file
                    or from the user created file.
                    It comes from SPARTAN_start_tui<==SPARTAN_configfile

        Returns
        ------
        """
        ###Make the input configuration an attribute of the class
        self.INPUT_CONF = INPUT_CONF


        ##check general:
        if check().check_General(self.INPUT_CONF.CONF) == 'Done':
            statusgen = 'Done'

        else:
            statusgen = check().check_General(self.INPUT_CONF.CONF)
        ###Check status of the spectroscopy and photometry section
        if self.INPUT_CONF.CONF['UseSpec'].lower() == 'no':
            ##if the config file says there is no need for spectroscopy
            statusspec = 'Not Needed'
        else:
            ##Else we check the input conf file
            statusspec = check().check_SPEC(self.INPUT_CONF.SPEC, self.INPUT_CONF.CONF['NSpec'])


        if self.INPUT_CONF.PHOT['Photo_file'] == '':
            ##If the input file says there is no magfile
            statusphot = 'Needed'
        else:
            statusphot = check().check_PHOT_startup(self.INPUT_CONF.PHOT)

        ##check the status of the lib section
        if self.INPUT_CONF.LIB['Type'] == 'provided':
            err, statusLIB = check().check_LibP(self.INPUT_CONF.LIB)
            del err
        elif self.INPUT_CONF.LIB['Type'] == 'created':
            err, statusLIB = check().check_LibP(self.INPUT_CONF.LIB)
            del err
        elif self.INPUT_CONF.LIB['Type'] == 'imported':
            err, statusLIB = check().check_LibP(self.INPUT_CONF.LIB)
            del err
        else:
            statusLIB = 'Needed'


        ###Initialize the Section array with section names and status
        self.Welcome_dic = [['Project General Configuration', statusgen], \
                          ['Spectroscopy', statusspec], \
                          ['Photometry', statusphot], \
                          ['Library', statusLIB], \
                          ['Cosmology', check().check_COSMO(self.INPUT_CONF.COSMO)], \
                          ['Fit & output', check().check_FIT(self.INPUT_CONF.FIT, \
                                self.INPUT_CONF.CONF['UsePhot'], self.INPUT_CONF.CONF['UseSpec'])]]


    def main(self):
        """
        This function creates the npyscreen.Form of the front page TUI.
        It first displays the welcome message and the SPARTAN Logo.
        Then it creates the 6 button to the other pages of the TUI.
        A status is associated to each button (displayed in red or green).

        When the OK button is hit, the check config program is started.

        parameters:
        ----------
        config_file: either the default SPARTAN empty template or
                     the config file passed to the code -c option

        Returns:
        ---------
        config:      the configuration of the run. A numpy array of 6 objects
                     each one having various attributes configuring the different
                     sections.

        """

        ###Get logo and welcome message
        self.Log = TUI_messages.Logo()
        wel = TUI_messages.welcome_mess()

        #get windows size from curses
        #to make the intialization of the
        #position right depending on the terminal size
        y, x = os.popen('stty size', 'r').read().split()
        self.x = int(x)
        self.y = int(y)

        # Change theme for dark terminal
        #npyscreen.setTheme(npyscreen.Themes.TransparentThemeLightText)

        # Initialize the form
        self.F = npyscreen.Form(name="SPARTAN configuration TUI", color='NO_EDIT')
        message = 'Welcome to '
        self.F.add(npyscreen.FixedText, value=message, relx=int((self.x-len(message))/2),\
                rely=int(2), editable=False, color='GOOD')

        ### Logo and welcome message, not editable
        j = 0
        for i in self.Log:
            ypos = int(self.y-7*self.y/8+j+1)
            self.F.add(npyscreen.FixedText, value=i, relx=int((self.x-len(i))/2),\
                    rely=ypos, editable=False, color='CURSOR')
            j += 1

        ypos += 1
        for i in wel:
            self.F.add(npyscreen.FixedText, value=i, relx=int((self.x-len(i))/2),\
                    rely=ypos, color='GOOD', editable=False)
            ypos += 1

        if ypos > (self.y)/2:
            posy = ypos+1
        else:
            posy = int(self.y/2)

        #### Conf Button
        A = len(self.Welcome_dic[0][0])  #get the size of the first section name
        B = len(self.Welcome_dic[0][1])  #get the size of the first section status word
        self.conf = self.F.add(npyscreen.ButtonPress, name=self.Welcome_dic[0][0], \
                relx=int((self.x-A-B)/3), rely=posy, color='STANDOUT')
        self.conf.whenPressed = self.buttontoconf
        self.statusconf = self.colorupdate(self.Welcome_dic[0][1])
        self.conft = self.F.add(npyscreen.FixedText, value=self.Welcome_dic[0][1],\
                 relx=-int((self.x-A-B)/2), rely=posy,\
                 editable=False, color=self.statusconf)

        posy += 1
        #### Spec Button
        self.spec = self.F.add(npyscreen.ButtonPress, name=self.Welcome_dic[1][0],\
                 relx=int((self.x-A-B)/3), rely=posy, color='STANDOUT')
        self.spec.whenPressed = self.buttontospec
        self.statusspec = self.colorupdate(self.Welcome_dic[1][1])
        self.spect = self.F.add(npyscreen.FixedText, value=self.Welcome_dic[1][1],\
                 relx=-int((self.x-A-B)/2), rely=posy,\
                 editable=False, color=self.statusspec)

        posy += 1
        #### Photo Button
        self.phot = self.F.add(npyscreen.ButtonPress, name=self.Welcome_dic[2][0],\
                 relx=int((self.x-A-B)/3), rely=posy, color='STANDOUT')
        self.phot.whenPressed = self.buttontophot
        self.statusphot = self.colorupdate(self.Welcome_dic[2][1])
        self.phott = self.F.add(npyscreen.FixedText, value=self.Welcome_dic[2][1],\
                 relx=-int((self.x-A-B)/2), rely=posy,\
                 editable=False, color=self.statusphot)
        posy += 1
        #### Lib Button
        self.Lib = self.F.add(npyscreen.ButtonPress, name=self.Welcome_dic[3][0],\
                 relx=int((self.x-A-B)/3), rely=posy, color='STANDOUT')
        self.Lib.whenPressed = self.buttontolib
        self.statusLib = self.colorupdate(self.Welcome_dic[3][1])
        self.Libt = self.F.add(npyscreen.FixedText, value=self.Welcome_dic[3][1],\
                 relx=-int((self.x-A-B)/2), rely=posy,\
                 editable=False, color=self.statusLib)

        posy += 1
        #### Cosmo Button
        self.Cosmo = self.F.add(npyscreen.ButtonPress, name=self.Welcome_dic[4][0],\
                 relx=int((self.x-A-B)/3), rely=posy, color='STANDOUT')
        self.Cosmo.whenPressed = self.buttontocosmo
        self.statusCosmo = self.colorupdate(self.Welcome_dic[4][1])
        self.Cosmot = self.F.add(npyscreen.FixedText, value=self.Welcome_dic[4][1],\
                 relx=-int((self.x-A-B)/2), rely=posy,\
                 editable=False, color=self.statusCosmo)

        posy += 1
        #### Fit button
        self.fit = self.F.add(npyscreen.ButtonPress, name=self.Welcome_dic[5][0],\
                 relx=int((self.x-A-B)/3), rely=posy, color='STANDOUT')
        self.fit.whenPressed = self.buttontofit
        self.statusfit = self.colorupdate(self.Welcome_dic[5][1])
        self.fitt = self.F.add(npyscreen.FixedText, value=self.Welcome_dic[5][1],\
                 relx=-int((self.x-A-B)/2), rely=posy,\
                 editable=False, color=self.statusfit)

        ### Add a space
        self.F.nextrely += 1

        ms = self.F.add(npyscreen.TitleSelectOne,\
                name="Start the fit after configuration?",labelColor='DANGER',\
                values=["NO", "YES"], value=0, scroll_exit=True, relx=int(self.x/3))

        ### to let people interact with the terminal
        self.F.edit()
        try:
            if ms.value[0] == 1:
                self.Startfit = 'yes'
            else:
                self.Startfit = 'no'
        except:
            self.Startfit = 'no'




    def buttontoconf(self):
        """
        Function that deals with the General configuration frame
        First it calls it, its attributes define the update of
        the self_CONF.CONF attribute. Then a check is performed
        to update the status of the section.
        Then the color of the section is changed, depending on
        the status.
        Additionaly, the spectroscopic and photometric section status
        are updated depending on the general configuration

        Parameters
        ----------

        Returns
        ---------
        """
        #Display the General conf frame
        C = conf.config_win(self.Log, self.x, self.y, self.INPUT_CONF.CONF)
        #Update the General configuration directory
        self.INPUT_CONF.CONF = C.__dict__
        #Check the General configuration
        status = check().check_General(self.INPUT_CONF.CONF)
        #Update the TUI front-frame dictionnary
        self.Welcome_dic[0][1] = status
        ###Update the status word of the section
        self.conft.value = self.Welcome_dic[0][1]
        ###Get the new color corresping to the status
        self.statusconf = self.colorupdate(self.Welcome_dic[0][1])
        ###Update the color of the section
        self.conft.color = self.statusconf
        self.conft.update()

        ###We also need to update the photometric configuration
        self.INPUT_CONF.PHOT['DataFile'] = self.INPUT_CONF.CONF['PCat']
        self.INPUT_CONF.PHOT['Phot'] = self.INPUT_CONF.CONF['UsePhot']
        self.INPUT_CONF.PHOT['Spec'] = self.INPUT_CONF.CONF['UseSpec']
        self.INPUT_CONF.PHOT['NSpec'] = self.INPUT_CONF.CONF['NSpec']

        ###Finally, we need to check what kind of data must be used
        ###And update the spectro and photo section colors accordingly
        ###SPECTROSCOPY
        if self.INPUT_CONF.CONF['UseSpec'].lower() == 'yes'\
                and (self.Welcome_dic[1][1] == 'Needed'\
                or self.Welcome_dic[1][1] == 'Done'):
            ###If user uses Spectroscopy but the spectroscopy is not configured yes
            ###or already configured, the color and status does not need to be changed
            pass

        if self.INPUT_CONF.CONF['UseSpec'].lower() == 'no':
            ###If the user do not need spectroscopy, therefore we must turn the
            ###section green and write 'not needed'
            specstatus = 'Not Needed'
            #We update the dictionnary
            self.Welcome_dic[1][1] = specstatus
            ###change the status word of the section
            self.spect.value = self.Welcome_dic[1][1]
            ### Get the color of the new status
            self.statusspec = self.colorupdate(self.Welcome_dic[1][1])
            self.spect.color = self.statusspec
            self.spect.update()
        if self.INPUT_CONF.CONF['UseSpec'].lower() == 'yes' \
                and self.Welcome_dic[1][1] == 'Not Needed':
            ###If the user needs spectroscopy but the status was on 'Not Needed'
            ###we must turn the section red and write 'Needed'
            specstatus = 'Needed'
            #We update the dictionnary
            self.Welcome_dic[1][1] = specstatus
            ###change the status word of the section
            self.spect.value = self.Welcome_dic[1][1]
            ### Get the color of the new status
            self.statusspec = self.colorupdate(self.Welcome_dic[1][1])
            self.spect.color = self.statusspec
            self.spect.update()

        if self.INPUT_CONF.CONF['UseSpec'].lower() == 'yes' and \
                check().check_SPEC(self.INPUT_CONF.SPEC, self.INPUT_CONF.CONF['NSpec']) == 'Done':
            ###If user needs spectroscopy but status was on 'Not Needed' while the
            ###spectroscopic configuration exists
            ###we must turn the section green and write 'Done'
            specstatus = check().check_SPEC(self.INPUT_CONF.SPEC, self.INPUT_CONF.CONF['NSpec'])
            #We update the dictionnary
            self.Welcome_dic[1][1] = specstatus
            ###change the status word of the section
            self.spect.value = self.Welcome_dic[1][1]
            ### Get the color of the new status
            self.statusspec = self.colorupdate(self.Welcome_dic[1][1])
            self.spect.color = self.statusspec
            self.spect.update()


    def buttontospec(self):
        """
        Function that deals with the SPectroscopic configuration frame
        First it calls it, its attributes define the update of
        the self_CONF.PHOT attribute. Then a check is performed
        to update the status of the section.
        Finally the color of the section is changed, depending on
        the status

        Parameters
        ----------

        Returns
        ---------
        """
        if self.INPUT_CONF.CONF['UseSpec'].lower() == 'yes' or \
                (self.spect.value in ['Needed', 'Incomplete']):

            #Display the Spectroscopic config frame
            S = spec.Spec_win(self.Log, self.x, self.y, self.INPUT_CONF.SPEC)
            #Update the General configuration directory
            self.INPUT_CONF.SPEC = S.__dict__
            #Check the General configuration
            status = check().check_SPEC(self.INPUT_CONF.SPEC, self.INPUT_CONF.CONF['NSpec'])
            #Update the TUI front-frame dictionnary
            self.Welcome_dic[1][1] = status
            ###Update the status word of the section
            self.spect.value = self.Welcome_dic[1][1]
            ###Get the new color corresping to the status
            self.statusspec = self.colorupdate(self.Welcome_dic[1][1])
            ###Update the color of the section
            self.spect.color = self.statusspec
            self.spect.update()




    def buttontofit(self):
        """
        Function that deals with the Photometric configuration frame
        First it calls it, its attributes define the update of
        the self_CONF.PHOT attribute. Then a check is performed
        to update the status of the section.
        Finally the color of the section is changed, depending on
        the status

        Parameters
        ----------

        Returns
        ---------
        """
        ##Call the Photometric frame model
        F = fit.Fit_win(self.Log, self.x, self.y, self.INPUT_CONF.FIT)
        #Update the General configuration directory
        self.INPUT_CONF.FIT = F.__dict__
        #Check the General configuration
        status = check().check_FIT(self.INPUT_CONF.FIT\
                 , self.INPUT_CONF.CONF['UsePhot'], self.INPUT_CONF.CONF['UseSpec'])
        #Update the TUI front-frame dictionnary
        self.Welcome_dic[5][1] = status
        ###Update the status word of the section
        self.fitt.value = self.Welcome_dic[5][1]
        ###Get the new color corresping to the status
        self.statusfit = self.colorupdate(self.Welcome_dic[5][1])
        ###Update the color of the section
        self.fitt.color = self.statusfit
        self.fitt.update()

    def buttontolib(self):
        """
        Function that deals with the Library configuration frame
        First it calls it, its attributes define the update of
        the self_CONF.LIB attribute. Then a check is performed
        to update the status of the section.
        Finally the color of the section is changed, depending on
        the status

        Parameters
        ----------

        Returns
        ---------
        """
        ##go to the frame
        L = lib.Welc_win(self.Log, self.x, self.y, self.INPUT_CONF.LIB)
        #Update the General configuration directory
        self.INPUT_CONF.LIB = L.__dict__['LIB_CONF']
        #Check the General configuration
        if self.INPUT_CONF.LIB['Type'] == 'provided':
            err, status = check().check_LibP(self.INPUT_CONF.LIB)
            del err
        elif self.INPUT_CONF.LIB['Type'] == 'created':
            err, status = check().check_LibP(self.INPUT_CONF.LIB)
            del err
        elif self.INPUT_CONF.LIB['Type'] == 'imported':
            err, status = check().check_LibP(self.INPUT_CONF.LIB)
            del err
        else:
            err = 'nop'
            status = 'Needed'

        #Update the TUI front-frame dictionnary
        self.Welcome_dic[3][1] = status
        ###Update the status word of the section
        self.Libt.value = self.Welcome_dic[3][1]
        ##Get the new color corresping to the status
        self.statusLib = self.colorupdate(self.Welcome_dic[3][1])
        ###Update the color of the section
        self.Libt.color = self.statusLib
        self.Libt.update()


    def buttontophot(self):
        """
        Function that deals with the Photometric configuration frame
        First it calls it, its attributes define the update of
        the self_CONF.PHOT attribute. Then a check is performed
        to update the status of the section.
        Finally the color of the section is changed, depending on
        the status

        Parameters
        ----------

        Returns
        ---------
        """
        ##Call the Photometric frame model
        P = phot.Phot_win(self.Log, self.x, self.y, self.INPUT_CONF.PHOT)
        #Update the General configuration directory
        self.INPUT_CONF.PHOT = P.__dict__
        #Check the General configuration
        status = check().check_PHOT(self.INPUT_CONF.PHOT)
        #Update the TUI front-frame dictionnary
        self.Welcome_dic[2][1] = status
        ###Update the status word of the section
        self.phott.value = self.Welcome_dic[2][1]
        ###Get the new color corresping to the status
        self.statusphot = self.colorupdate(self.Welcome_dic[2][1])
        ###Update the color of the section
        self.phott.color = self.statusphot
        self.phott.update()



    def buttontocosmo(self):
        """
        Function that deals with the Cosmo configuration frame
        First it calls it, its attributes define the update of
        the self_CONF.COSMO attribute. Then a check is performed
        to update the status of the section.
        Finally the color of the section is changed, depending on
        the status

        Parameters
        ----------

        Returns
        ---------
        """
        ##Call the Cosmological frame model
        C = cosmo.Cosmo_win(self.Log, self.x, self.y, self.INPUT_CONF.COSMO)
        #Update the General configuration directory
        self.INPUT_CONF.COSMO = C.__dict__
        #Check the General configuration
        status = check().check_COSMO(self.INPUT_CONF.COSMO)
        #Update the TUI front-frame dictionnary
        self.Welcome_dic[4][1] = status
        ###Update the status word of the section
        self.Cosmot.value = self.Welcome_dic[4][1]
        ###Get the new color corresping to the status
        self.statusCosmo = self.colorupdate(self.Welcome_dic[4][1])
        ###Update the color of the section
        self.Cosmot.color = self.statusCosmo
        self.Cosmot.update()


    def colorupdate(self, status):
        """
        This function determines the color of the status of the section

        Paramters:
        ---------
        status  string type, status of section (Needed, Incomplete,
                Not Needed, Default,Done)

        Return:
        ------
        Color   string type, gives the color of the section to be
                displayed ('LABEL','CURSOR')
        """
        Good_status = ['Default', 'Done', 'Not Needed']

        Bad_status = ['Needed', 'Incomplete', 'Unset',\
                    'Bad Number CPU', 'Bad Number Node', 'No Project Name',\
                    'No Project dir', 'Catalog not found', 'No datatype',\
                    'No Mag System', 'No Filter Set', 'No Magnitude to Fit',\
                    'No Magnitude Norm', 'No Project Directory',\
                    'No datafile', 'Invalid Mag File', 'Incompatible file',\
                    'No Mag File', 'Use Cosmo?', 'Sum Parameter dif 1', 'Ho<0?', \
                    'Edges neg', 'Nedge != Nspec', 'Pb Bad Regions', "Bad 'Bad regions'", \
                    'No Bad Regions given', 'No spec. resol. given', 'NRes != Nspec',\
                    'Negative Resolution!', 'No Norm Spec regions File given', 'Nregions != NSpec',\
                    'one regions is badly defined', 'region badly defined:l0>l1', \
                    'Bad spectra directory']

        if status in Bad_status:
            color = 'CRITICAL'
        if status in Good_status:
            color = 'GOOD'

        return color
