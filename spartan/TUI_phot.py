'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
##### TUI photometry Frame
#####     configuration
#####
#####
############################
@License: GPLv3 - see LICENCE.txt
'''
####Third party##
import npyscreen
###################

####Local imports
from .config_check       import check
from .photometry_filters import Retrieve_Filter_inf as RET

class Phot_win:
    """
    This class manages the photometry section of the TUI: the photometry configuration

    Attributes:
        self.System         Filter System to be used
        self.Photo_config   Photometric configuration
        self.Ph             Npyscreen form of the section
    """
    def __init__(self, Log, x, y, PHOT):
        """
        Class constructor creating the form and populating it with widgets
        Parameters:
        ----------
        PHOT:   A dictionnary containing the information of each widget
                It can be empty or coming from an already defined Project
                Format={Data file, FilterSystem}
                Types={str,int}

        Log:    SPARTAN LOGO to be drawn at the top of the form

        x,y:    size of the front page of the TUI. The new page descibed here
                is drawn on the same size.

        Returns:
        -------
        """
        ###Load the filter list
        Filters = RET().filter_list()
        ##Initialize form and write logo
        self.L1 = npyscreen.Form(name="SPARTAN Photometry configuration", \
                color='STANDOUT')
        ### Write the Logo
        for i in Log:
            self.L1.add(npyscreen.FixedText, value=i,\
                     relx=int((x-len(i))/2), editable=False)

        ###Make the box
        n = 8 ###Terminal row zhere we draw the boxes
        self.L1.add(npyscreen.BoxBasic, name='Photometry', rely=n, \
                editable=False, color='DANGER')


        ####extract file from PATH/FILE
        ##Check if a datafile name is given
        FILE, DataMag = check().check_datafile(PHOT['DataFile'], \
                PHOT['Spec'], PHOT['Phot'], PHOT['NSpec'])

        ####Populate the form with widgets
        self.L1.add(npyscreen.TitleText, name='Data file',\
                 relx=3, rely=n+1, max_width=40, value=FILE, max_heigth=1, editable=False)

        ###Extract file name from magfile
        Filemag, FilemagData = check().check_magfile_stru(PHOT['Photo_file'])
        self.L1.add(npyscreen.TitleText, name='Mag conf',\
                relx=3, rely=n+2, max_width=40, value=Filemag, \
                max_heigth=1, editable=False)

        ##Check if the filter configuration exist
        if len(PHOT['Photo_config']) == 0 and len(FilemagData) == 0:
            Photo = []

        elif len(PHOT['Photo_config']) != 0:
            Photo = PHOT['Photo_config']

        elif len(FilemagData) != 0:
            Photo = FilemagData


        ###Magnitude System
        if  PHOT['System'].lower() == 'ab':
            SYSTEM = 0

        elif  PHOT['System'].lower() == 'jy':
            SYSTEM = 1

        else:
            SYSTEM = ''

        System = self.L1.add(npyscreen.TitleSelectOne, \
                value=[SYSTEM], name="System", values=["AB", "Jy"]\
                , scroll_exit=True, relx=int(x/2)+4, rely=n+1, \
                max_height=2, max_width=30)

        self.L1.add(npyscreen.FixedText, relx=3, rely=n+3,\
                 max_width=int(x/2)-1,\
                 value='data  Filter  Fit   Out   Abs  Nor',\
                 max_heigth=1, editable=False, color='DANGER')

        self.L1.add(npyscreen.FixedText, relx=int(x/2)-1, rely=n+3,\
                 max_width=int(x/2)-3, \
                 value='data  Filter  Fit   Out   Abs  Nor',\
                 max_heigth=1, editable=False, color='DANGER')

        #### Make all the magnitude lines
        ys = n+4
        xs = 3

        FULL_FILTERS = []
        for i in enumerate(DataMag):
            index = i[0]
            m = i[1]
            fil = self.oneFilter(index,m , Filters, xs, ys, self.L1, Photo)
            FULL_FILTERS.append(fil)
            ys += 1
            if ys == y-3:
                xs = int(x/2)-1
                ys = n+4

        ###To let the user interact with the screen
        self.L1.edit()

        ###Extract the Filter informations
        Photo_config = []
        for f in FULL_FILTERS:
            ##For each filter we create a disctionnary
            ONE_FILT = {'name':'', 'Filter':'', 'Fit':'', 'Out':'', 'Abs':'', 'Nor':''}
            ##And then we update it with the value from the widgets
            #First we need the name of the magnitude from the data file
            ONE_FILT['name'] = f[0].value
            ##Then the filter
            if f[1].value == '':
                #if filter name was not set We skip this filter
                ONE_FILT['Filter'] = 'NoFilt'
                ONE_FILT['Fit'] = 'No'
                ONE_FILT['Out'] = 'No'
                ONE_FILT['Abs'] = 'No'
                ONE_FILT['Nor'] = 'No'

            else:
                #if filter name was set we look at the widget values
                ONE_FILT['Filter'] = Filters[int(f[1].value)]
                if f[2].value is True:
                    ONE_FILT['Fit'] = 'yes'
                else:
                    ONE_FILT['Fit'] = 'no'

                if f[3].value is True:
                    ONE_FILT['Out'] = 'yes'
                else:
                    ONE_FILT['Out'] = 'no'

                if f[4].value is True:
                    ONE_FILT['Abs'] = 'yes'
                else:
                    ONE_FILT['Abs'] = 'no'

                if f[5].value is True:
                    ONE_FILT['Nor'] = 'yes'
                else:
                    ONE_FILT['Nor'] = 'no'

            Photo_config.append(ONE_FILT)

        ###Define the attributes of the class
        if System.value[0] == 0:
            self.System = 'AB'
        elif System.value[0] == 1:
            self.System = 'Jy'
        else:
            self.System = 'AB'

        self.Photo_config = Photo_config
        self.DataFile = PHOT['DataFile']
        self.Spec = PHOT['Spec']
        self.Phot = PHOT['Phot']
        self.NSpec = PHOT['NSpec']
        self.Photo_file = PHOT['Photo_file']

    def oneFilter(self, index, Mag, Fillist, xs, ys, Form, Photo):
        """
        Function that draw a filter line.
        It displays the name of the magnitude followed by the list
        of filter in a dropdown list and 4 boxes (Fit/out/Abs/Norm)

        Parameters
        ----------
        index:      index(line) of the magnitude in the magnitude file
        Mag:        Name of the magnitude as specified in the input catalog
        Fillist:    Filter list from the filter file
        xs:         x-position of the line
        ys:         y-position of the line
        Form:       Form of the section.
        FilemagData Information from the Filemag configuration


        Returns:
        -------
        filter_config:  array of the name of the magnitude and all the widgets.
                        Done to be able to retrieve data for each filters

        """
        DataMag = Form.add(npyscreen.FixedText, relx=xs, \
                rely=ys, value=Mag, max_heigth=1, max_width=6, editable=False)

        Magfromconfig = []
        for i in Photo:
            Magfromconfig.append(i['name'])

        if len(Photo) != 0 and (Mag in Magfromconfig):

            N = index

            if Photo[N]['Filter'] in Fillist:
                ##if the filter from the magfile is in the filter list
                Filter = Form.add(npyscreen.ComboBox,\
                     relx=xs+6, rely=ys, max_width=6, max_heigth=1,\
                     values=Fillist, value='value')
                ###Update the value of the widget
                for i in range(len(Fillist)):
                    if Fillist[i] == Photo[N]['Filter']:
                        Filter.value = i
                        Filter.update()
            else:
                ##If the filter is not in the filelist
                Filter = Form.add(npyscreen.ComboBox,\
                     relx=xs+6, rely=ys, max_width=6, max_heigth=1, values=Fillist)


            Fit = Form.add(npyscreen.CheckboxBare, \
                     scroll_exit=True, rely=ys, relx=xs +14,\
                     value=self.bool_to_bool(Photo[N]['Fit']))

            out = Form.add(npyscreen.CheckboxBare, \
                    scroll_exit=True, rely=ys, relx=xs +20,\
                     value=self.bool_to_bool(Photo[N]['Out']))

            Abs = Form.add(npyscreen.CheckboxBare, \
                    scroll_exit=True, rely=ys, relx=xs +26,\
                     value=self.bool_to_bool(Photo[N]['Abs']))

            Norm = Form.add(npyscreen.CheckboxBare, \
                    scroll_exit=True, rely=ys, relx=xs +31,\
                     value=self.bool_to_bool(Photo[N]['Nor']))

        else:
            ## if the magnitude is not in the magfile
            Filter = Form.add(npyscreen.ComboBox,\
                     values=Fillist, relx=xs+6, rely=ys, max_width=6, max_heigth=1)

            Fit = Form.add(npyscreen.CheckboxBare, \
                    scroll_exit=True, rely=ys, relx=xs +14, value=True)

            out = Form.add(npyscreen.CheckboxBare, \
                    scroll_exit=True, rely=ys, relx=xs +20, value=True)

            Abs = Form.add(npyscreen.CheckboxBare, \
                    scroll_exit=True, rely=ys, relx=xs +26, value=True)

            Norm = Form.add(npyscreen.CheckboxBare, \
                    scroll_exit=True, rely=ys, relx=xs +31)

        filter_config = [DataMag, Filter, Fit, out, Abs, Norm]

        return filter_config

    def bool_to_bool(self, A):
        """
        Function that converts yes or no to True or False

        Parameter
        ---------
        A       yes or no

        Return
        ------
        Bool    True or False

        """
        if A.lower() == 'yes':
            return True

        elif A.lower() == 'no':
            return False

        else:
            return False
