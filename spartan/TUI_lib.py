'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
#####   File of the lib
#####       page TUI
#####
###########################
'''
###Python libs
import npyscreen

#######
from .             import TUI_lib_Provided as libProvided
from .config_check import check

class Welc_win:
    '''
    This class draws the welcome frame of libraries
    '''
    def __init__(self, Log, x, y, LIB_CONF):

        self.x = x
        self.y = y
        self.Log = Log
        self.LIB_CONF = LIB_CONF

        ##Initialize form and write logo
        self.L1 = npyscreen.Form(name="SPARTAN Fitting library", color='STANDOUT')

        for i in self.Log:
            self.L1.add(npyscreen.FixedText, value=i, relx=int((x-len(i))/2), editable=False)

        n = 9
        ###Make the boxes
        self.L1.add(npyscreen.BoxBasic, name='Type of construction', rely=n, \
                max_width=int(x/2)-1, editable=False, color='DANGER')
        self.L1.add(npyscreen.BoxBasic, name='Additional informations', \
                relx=int(x/2)+1, rely=9, editable=False, color='DANGER')

        ### Populate with widgets
        ### left column:Button
        n = 11
        self.L1.add(npyscreen.FixedText, value='(One choice only)', relx=10,\
                rely=n, max_width=int(x/3), editable=False)

        ###########LIB P
        ##first we check if the user uses this type
        self.ProvidedType = self.check_type(LIB_CONF['Type'], 'provided')
        ## then we create the button
        self.Provided = self.L1.add(npyscreen.ButtonPress, name='Use Provided models',\
                 color=self.ProvidedType, relx=3, rely=n+int((y-n)/4))
        ##and define the action
        self.Provided.whenPressed = self.buttontoProvided
        ##check the status of the section
        self.ProvidedStatus, status = check().check_LibP(self.LIB_CONF)
        #del status
        ##write the status
        self.statustextPro = self.L1.add(npyscreen.MultiLineEdit, value=self.ProvidedStatus, \
                relx=4, rely=n+int((y-n)/4)+1, max_width=int(x/2.5), max_height=1, editable=False,\
                 color=self.check_status(self.ProvidedStatus))

        ############LIB C
        self.CreateStatus = self.check_type(LIB_CONF['Type'], 'created')
        self.Create = self.L1.add(npyscreen.ButtonPress, name='Create your own [NOT YET AVAILABLE]',\
                 color=self.CreateStatus, relx=3, rely=n+2*int((y-n)/4))
        self.Create.whenPressed = self.buttontoCreate
        self.CreateStatus = '-->Incomplete'
        self.L1.add(npyscreen.MultiLineEdit, value=self.CreateStatus, relx=4, \
                rely=n+2*int((y-n)/4)+1, max_width=int(x/2.5), editable=False, color='CRITICAL')

        ############LIB I
        self.ImportType = self.check_type(LIB_CONF['Type'], 'imported')
        self.Import = self.L1.add(npyscreen.ButtonPress, name='import models [NOT YET AVAILABLE]',\
                 color=self.ImportType, relx=3, rely=n+3*int((y-n)/4))
        self.Import.whenPressed = self.buttontoImport
        self.ImportStatus = '-->Incomplete'
        self.L1.add(npyscreen.MultiLineEdit, value=self.ImportStatus, relx=4, \
                rely=n+3*int((y-n)/4)+1, max_width=int(x/2.5), editable=False, color='CRITICAL')


        ###right column :Text
        v = '3 options are available: \n\n\n1-You create a Library from the \nSPARTAN models [Use].\n\n\n\
2-Create your own library inside \nSPARTAN[Create] \n\n\n3- Import your own Library (see\nManual) for the SPARTAN library\nformat[Import]. \n'
        self.L1.add(npyscreen.MultiLineEdit, value=v, relx=int(x/2)+2, rely=n,\
                 max_width=int(x/2.5), editable=False)
        #######


        self.L1.edit()

    def check_type(self, typeL, section):
        """
        Function that checks the type to give the color to each section

        Parameter
        ---------
        status  str, status from the input conf file

        Return
        ------

        color   str, color to be displayed
        """
        if typeL == section:
            return 'GOOD'

        else:
            return 'CRITICAL'



    def check_status(self, status):
        """
        Function that checks the status to be given to each section

        Parameter
        ---------
        status  str, status from the check of the conf file

        Return
        ------
        color   str, color to be displayed
        """
        if status in ['ok', 'Done']:
            return 'GOOD'
        else:
            return 'CRITICAL'


    def buttontoProvided(self):
        """
        Function that display the frame that uses prebuild SSPs.
        First it calls it, its attributes define the update of
        the XXX attribute. Then a check is performed to update the status of the section.
        Then the color of the section is changed, depending on the status

        Parameter
        --------

        Return
        ------
        """
        P = libProvided.LibProvided_win(self.Log, self.x, self.y, self.LIB_CONF)
        self.LIB_CONF = P.__dict__
        ###remove useless keywords:
        self.LIB_CONF.pop('LibP', None)
        self.LIB_CONF.pop('x', None)
        self.LIB_CONF.pop('y', None)
        self.LIB_CONF['Type'] = 'provided'

        if self.LIB_CONF['Param'] != {}:
            ##extract params of the base
            for i in self.LIB_CONF['Param']['Parameter'].keys():
                self.LIB_CONF[i] = self.LIB_CONF['Param']['Parameter'][i][:-2].replace('\n', '')
            ##the [:-2] is to remove the '\n' at the end of the line

            ##remove the total parambase dictionnary
            self.LIB_CONF.pop('Param')
        else:
            self.LIB_CONF['Age'] = ''
            self.LIB_CONF['TAU'] = ''
            self.LIB_CONF['MET'] = ''

        ##global check
        err, status = check().check_LibP(self.LIB_CONF)

        ##update stats and color
        self.Provided.color = 'GOOD'
        self.Provided.update()
        self.statustextPro.value = err
        self.statustextPro.color = self.check_status(status)
        self.statustextPro.update()


    def buttontoCreate(self):
        '''
        Function that displays the frame that build CSPs.
        First it calls it, its attributes define the update of
        the XXX attribute. Then a check is performed to update the status of the section.
        Then the color of the section is changed, depending on the status

        '''
        #R=libCreate.LibCreate_win(self.Log,self.x,self.y,LIB)
        self.LIB_CONF['Type'] = 'Creates'

    def buttontoImport(self):
        '''
        Function that display the frame that allows the importation of libraries.
        First it calls it, its attributes define the update of
        the XXX attribute. Then a check is performed to update the status of the section.
        Then the color of the section is changed, depending on the status

        '''
        #I = libImport.LibImport_win(self.Log, self.x, self.y, LIB)
        self.LIB_CONF['Type'] = 'Imported'



    def colorupdate(self, status):
        """
        This function determines the color of the status of the section

        Paramters:
        ---------
        status  string type, status of section (Needed,Default,Done)

        Return:
        ------
        Color   string type, gives the color of the section to be displayed ('LABEL','CURSOR')
        """
        if status == 'Needed' or status == 'Incomplete':
            color = 'CRITICAL'

        if status == 'Default' or status == 'Done' or status == 'Not Needed':
            color = 'GOOD'

        return color
