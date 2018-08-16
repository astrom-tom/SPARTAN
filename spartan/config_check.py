'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
##### File that checks the
#####     configuration
#####
#####
############################
@License: GPL licence - see LICENCE.txt
'''

##Python General Libraries
import os
import numpy

## SPARTAN Modules
from . import messages as MTU
from .config_file import read_config
from .read_data_file import extract_mag_names as Mags_list
from .input_spartan_files import sp_input_files as PIF
from .TUI_spec import specunits
from .TUI_lib_Provided import check_param_base as CPB
from .Lib_provided import Retrieve_Lib_info as Retr

class check:
    """
    class that checks each part of the conffiguration
    It is used by the TUI itself and also from the
    'SPARTAN -c' command
    """

    def check_General(self, Dico):
        """
        Functions that check the general configuration
        section of the project

        Parameters
        ----------
        Dico    A dictionnary containing the information of each widget
                It can be empty or coming from an already defined
                Format={Project Name, Author,Project directory, Date,\
                Number of nodes, Number of CPU,Usespec, Usephot}

        Returns
        -------
        status  Status word (string)

        """

        ###We check the mandatory fields only:
        Mandatory = 0

        if Dico['NCPU'] and int(Dico['NCPU']) > 0:
            Mandatory += 1
        else:
            return 'Bad Number CPU'

        if Dico['PName'] != '':
            Mandatory += 1
        else:
            return 'No Project Name'

        if Dico['PDir'] != '':
            Mandatory += 1
        else:
            return 'No Project dir'

        if os.path.isfile(Dico['PCat']):
            Mandatory += 1
        else:
            return 'Catalog not found'

        #Check if at least one type of data is selected
        if Dico['UsePhot'].lower() == 'yes' or Dico['UseSpec'].lower() == 'yes':
            Mandatory += 1
        else:
            return 'No datatype selec'
        
        if Dico['UseSpec'].lower() == 'yes':
            if Dico['NSpec'] == '':
                return 'Incomplete'
            if int(Dico['NSpec']) < 0:
                return 'Incomplete'

        if Mandatory == 5:
            ##If everything is fine
            return 'Done'

        elif Mandatory < 2:
            ###For the default file
            return 'Needed'

        elif Mandatory != 6:
            ##If something is missing
            return 'Incomplete'

    def check_SPEC(self, Dico, Nspec):
        """
        Functions that check the spectroscopic configuration
        section of the project

        Parameters
        ----------
        Dico    A dictionnary containing the information of each widget
                It can be empty or coming from an already defined
                Format={Spectra directory, Use Full,binning, specz,\
                        Funits, Wunits,Skip, Sizeskip,Use BR,Bad Regions}
                Types={str,int,str,int,str,str,int,str,int,str}
        Returns
        -------
        status  Status word (string)

        """
        Mandatory = 0
        if os.path.isdir(Dico['SDir']):
            Mandatory += 1
        else:
            return 'Bad spectra directory'

        if Dico['Res']!='':
            #if one spectrum only
            if float(Nspec) == 1.:
                if float(Dico['Res'])>0:
                    Mandatory +=1

            ###If more than one spectrum
            elif float(Nspec)>1:
                R = Dico['Res'].split(';')

                ##if Nspec != NRes
                if len(R) != int(Nspec):
                    return 'NRes != Nspec'

                ##we check that the values are all positive
                for i in R:
                    if float(i) < 0:
                        return 'Negative Resolution!'
                ##if we passed all the checks we ARE OK
                Mandatory+=1
        else:
            return 'No spec. resol. given'

        if Dico['Skip'].lower() == 'yes':
            try:
                ##if the user want to skip edge but did not give any
                ## value
                if Dico['SSkip'] == '':
                    return 'Incomplete'
                 
                ###if more than one spectra
                elif float(Nspec) > 1.:
                    Ed = Dico['SSkip'].split(';')

                    ##if Nspec != Nedge
                    if len(Ed) != int(Nspec):
                        return 'Nedge != Nspec'

                    ##we check that values are all positive
                    for i in Ed:
                        if float(i)<0:
                            return 'Edges neg'

                    ###if we passed all the checks
                    Mandatory += 1 

                #if only one spectrum we check that the value is positive 
                elif float(Nspec) == 1.:
                    if float(Dico['SSkip']) < 0:
                        return 'Edges neg'
                    else:
                        Mandatory += 1 
                else:
                    pass
            except:
                return 'Incomplete'

        else:
            Mandatory += 1
        
        if Dico['UseBR'].lower() == 'yes':
            try:
                if Dico['BR'] == '':
                    return 'No Bad Regions given'

                else:
                    br = Dico['BR'].split(';')
                    for i in br:
                        indiv = i.split('-')
                        ##a bad region must contain 2 elements
                        if len(indiv) != 2:
                            Mandatory -= 1
                            return "Bad 'Bad regions'"
                        elif float(indiv[1]) <= float(indiv[0]):
                            return 'Incomplete'
                        else:
                            ##each part must be positive
                            if float(indiv[0]) < 0:
                                return 'Incomplete'
                            elif float(indiv[1]) < 0:
                                return 'Incomplete'
                    ##if we passed all the checks
                    Mandatory += 1
            except:
                return 'Pb Bad Regions'

        else:
            Mandatory += 1

        ###From here we check the units
        ###we must check is the we have a list or a string
        if type(Dico['Funit']) == list and len(Dico['Funit'])>0:
            if Dico['Funit'][0] in specunits().Funitchoice:
                Mandatory += 1
            else:
                Mandatory -= 1

        elif type(Dico['Funit']) == str:
            if Dico['Funit'] in specunits().Funitchoice:
                Mandatory += 1
            else:
                Mandatory -= 1

        ###Idem for the wavelength
        if type(Dico['Wunit']) == list and len(Dico['Wunit'])>0:
            if Dico['Wunit'][0] in specunits().Wunitchoice:
                Mandatory += 1
            else:
                Mandatory -= 1

        elif type(Dico['Wunit']) == str:
            if Dico['Wunit'] in specunits().Wunitchoice:
                Mandatory += 1
            else:
                Mandatory -= 1

        ##check calibration fit
        if Dico['Calib'].lower() == 'yes':
            Mandatory += 1
        else:
            Mandatory += 1
        
        ###check normalisation method
        if Dico['Norm'] == 'mags':
            Mandatory += 1

        if Dico['Norm'] == 'region':
            regions  = Dico['Norm_reg'].split(';')
            if float(Nspec) != len(regions):
                return 'Nregions != NSpec'
            else:
                for i in range(len(regions)):
                    indiv = regions[0].split('-')
                    if len(indiv) == 2 :
                        if indiv[0] >= indiv[1]:
                            return 'region badly defined:l0<l1'

                ###if we passed all the checks
                Mandatory += 1

        if Mandatory == 8:
            ##If everything is fine
            return 'Done'

        elif Mandatory <= 2:
            ###For the default file or when the major part is missing
            return 'Needed'

        elif Mandatory != 8:
            ##If something is missing
            return 'Incomplete'
        
        else:
            return 'Incomplete'

    def check_PHOT_startup(self, Dico):
        """
        Functions that check the photometric configuration
        at startup

        Parameters
        ----------
        Dico    A dictionnary containing the information of each widget
                It can be empty or coming from an already defined
                Format={Magfile, FilterSystem}
                Types={str,int}

        Data    input data file
        usespec if the user wants to use spec
        nspec   number of spec to be used
        usephot if the user wants to use phot

        Returns
        -------
        status  Status word (string)
        """
        try:
            ##First we retrieve the magnitudes name from the datafile
            FIle, Mags = self.check_datafile(Dico['DataFile'], Dico['Spec'], \
                    Dico['Phot'], Dico['NSpec'])
            del FIle
        except:
            return 'No datafile'
        try:
            ##Then we try to load the magfile
            Datamag = numpy.genfromtxt(Dico['Photo_file'], dtype='str').T
        except:
            return 'Needed'

        ##Quick structure check
        if len(Datamag) == 0:
            return 'No Mag File'


        if len(Datamag) != 6:
            return 'Invalid Mag File'

        ##Then we check if the names from the magfile are the same
        ## as the names of the datafile and that at least one filter is
        ## set
        Magsfrommagfile = Datamag[0]
        filters = Datamag[1]
        bad = 0
        filt = 0

        ###if we have only one magnitude both in the magfile
        ##and in the data catalog
        if  Magsfrommagfile.size ==1 and  len(Mags) == 1:
            if Magsfrommagfile == Mags[0]:
                filt += 1 

        ### if the number of magnitude in the catalog of data
        ### is different from the number of filter in the magfile
        elif Magsfrommagfile.size != len(Mags):
            return 'Incompatible file'

        ###if we have more than one photometric point
        if Magsfrommagfile.size > 1 and len(Mags)>1:
            for i, j in zip(Magsfrommagfile, filters):
                if i not in Mags:
                    bad += 1

                if j != 'NoFilt':
                    filt += 1

        if bad == 0 and filt != 0:
            return 'Done'
        elif bad == 0 and filt == 0:
            return 'No Filter Set'
        else:
            return 'Incompatible file'

    def check_PHOT(self, Dico):
        """
        Functions that check the photometric configuration
        section of the project

        Parameters
        ----------
        Dico    A dictionnary containing the information of each widget
                It can be empty or coming from an already defined
                Format={Data file, FilterSystem}
                Types={str,int}

        Returns
        -------
        status  Status word (string)
        """
        Mandatory = 0

        if Dico['System']:
            Mandatory += 1
        else:
            return 'No Mag System'

        Norm = 0
        Fit = 0
        Filt = 0
        for i in Dico['Photo_config']:
            if i['Nor'].lower() == 'yes':
                Norm += 1
            if i['Fit'].lower() == 'yes':
                Fit += 1
            if i['Filter'].lower() != 'nofilt':
                Filt += 1

        if Filt != 0:
            Mandatory += 1
        else:
            return 'No Filter Set'

        if Fit != 0:
            Mandatory += 1
        else:
            return 'No Magnitude to Fit'

        if Norm != 0:
            Mandatory += 1

        else:
            return 'No Magnitude Norm'

        if Mandatory == 4:
            ##If everything is fine
            return 'Done'

        elif Mandatory <= 2:
            ###For the default file
            return 'Needed'

        elif Mandatory != 4:
            ##If something is missing
            return 'Incomplete'

        return 'Incomplete'


    def check_FIT(self, Dico, usephot, usespec):
        """
        Functions that check the fit configuration
        section of the project

        Parameters
        ----------
        Dico    A dictionnary containing the information of each widget
                It can be empty or coming from an already defined
                 Format={Algo,Overfit, Decision Tree, colorsDR,PDFvalues,\
                         BestFitValues,KeepPDF,WeightsMethod,WeightsPerso}
                 Types={int,int,int,str,int,int,int,int,str}

        usespec use of the spectroscopy
        usephot use of the photonetry

        Returns
        -------
        status  Status word (string)

        """
        ###We check only the mandatory fields
        Mandatory = 0

        ###We check default configuration
        if Dico['Algo'].lower() == 'chi2' and Dico['OverFit'].lower() == 'no' and \
                Dico['PDFV'].lower() == 'yes' and Dico['BFV'].lower() == 'yes' and \
                Dico['Combined'] == 'complementary':
            return 'Default'

        if Dico['Algo'] == '':
            return 'Incomplete'
        elif not Dico['Algo'] in ["CHI2", "MCMC(soon)"]:
            return 'Incomplete'
        else:
            Mandatory += 1

        if Dico['OverFit']:
            Mandatory += 1

        if Dico['Algo']:
            Mandatory += 1

        if Dico['PDFV'] == '' and Dico['BFV'] == '':
            ###if the user didnt precise either PDF values
            ### or best fit values
            Mandatory -= 1


        if Dico['PDFV'].lower() == 'yes' or Dico['BFV'].lower() == 'yes':
            ###One of the 2 is sufficient
            Mandatory += 1

        if usephot.lower() == 'yes' and usespec.lower() == 'yes':
            if Dico['Combined'] == '':
                return 'Incomplete'

            elif Dico['Combined'].lower() not in ["complememtary", "full"]:
                return 'Incomplete'

            else:
                Mandatory +=1
        else:
            Mandatory += 1

        if Mandatory == 5:
            ##If everything is fine
            return 'Done'

        elif Mandatory <= 2:
            ###For the default file
            return 'Needed'

        elif Mandatory != 5:
            ##If something is missing
            return 'Incomplete'

    def check_COSMO(self, Dico):
        """
        Functions that check the cosmological configuration
        section of the project

        Parameters
        ----------
        Dico    A dictionnary containing the information of each widget
                It can be empty or coming from an already defined
                Format={Ho, Omega_m, Omega_L,UseCosmo}
                Types={str,str,str,int}
        Returns
        -------
        status  Status word (string)
        """

        ###We check the mandatory fields only:
        Mandatory = 0

        if Dico['UseCo'].lower() == 'no':
            ##If the user does not use cosmology, no need to check further
            ## the cosmological models
            return 'Done'

        elif Dico['UseCo'].lower() == 'yes':
            ###If the user uses cosmology, we need to check the the parameters
            Mandatory += 1

            if float(Dico['Omega_L'])+float(Dico['Omega_m']) == 1:  ##Check that the sum is =1
                Mandatory += 1
            else:
                return 'Sum Parameter dif 1'


            if float(Dico['Ho']) > 0: ## check is hubble parameter >0
                Mandatory += 1
            else:
                return 'Ho<0?'


            if Mandatory == 3 and float(Dico['Omega_L']) == 0.73 and\
                    float(Dico['Omega_m']) == 0.27 and float(Dico['Ho']) == 70:
                ##Check if we still have thedefault configuration
                return 'Default'

            elif Mandatory == 3 and (float(Dico['Ho']) != 70 or \
                    float(Dico['Omega_L']) != 0.73 or float(Dico['Omega_m']) != 0.27):
                ## If everything is good but does not corresponds to the
                ## default configuration
                return 'Done'

            if Mandatory != 3:
                ##If something is missing
                return 'Incomplete'

        else:
            ##if the user did not specify if the cosmo must be used or not
            return 'Use Cosmo?'

    def check_LibP(self, Dico):
        """
        Functions that checks the LibP configuration
        section of the project

        Parameters
        ----------
        Dico    A dictionnary containing the information of each widget
                It can be empty or coming from an already defined configuration
                Format={}
                Types={}
        Returns
        -------
        status  Status word (string)
        """

        Mandatory = 0

        ###IGM
        if Dico['IGMtype'].lower() not in ['mean_meiksin', 'mean_madau', 'none',\
                'free_madau', 'free_meiksin']:
            return 'IGM not selected', 'Incomplete'
        else:
            Mandatory += 1

        ##EMLINE
        if Dico['EMline'].lower() not in ['yes', 'no']:
            return 'EM line type not selected', 'Incomplete'
        else:
            Mandatory += 1

        ###DUST
        EXT_list_files = PIF().Dust()
        Ext_list = numpy.genfromtxt(EXT_list_files, dtype='str').T
        Extdir = os.path.dirname(EXT_list_files)
        ##populate the list of name from the list in the ext file
        list_ext = []
        list_ext.append("none")
        for i in Ext_list:
            if os.path.isfile(os.path.join(Extdir, i)) is True:
                list_ext.append(i[:-4].lower())

        ##first we check if the selected name is in the list of possibilities
        if Dico['DustUse'].lower() not in list_ext:
            return 'Dust extinction not selected', 'Incomplete'
        else:
            ##if it is 'None'we stop here the dust checking
            if Dico['DustUse'].lower() == 'none':
                Mandatory += 1
            else:
                ##if it is different from 'none' we try to split the list
                try:
                    EBValue = Dico['EBVList'].split(';')
                except:
                    return 'Wrong format fot EBV list', 'Incomplete'
                ###if it works we convert them all to float
                try:
                    Values = [float(i) for i in EBValue]
                except:
                    return 'Wrong characters in EBV list', 'Incomplete'

                #finally we check if they are all positive values
                if all(i >= 0 for i in Values):
                    Mandatory += 1
                else:
                    return 'Negative number for EBV?', 'Incomplete'

        ##Base SSP:
        LIB_list_files = PIF().Base_LibP()
        Lib_list = numpy.genfromtxt(LIB_list_files, dtype='str').T
        Libdir = os.path.dirname(LIB_list_files)
        #Populate the list of name from the list in the SSPbase file
        list_buttons = []
        for i in Lib_list:
            if os.path.isfile(os.path.join(Libdir, i)) is True:
                list_buttons.append(i[4:-5])

        if Dico['BaseSSP'] not in list_buttons:
            return 'The SSP base name is not recognized', 'Incomplete'

        else:
            Basename = 'LIB_'+Dico['BaseSSP']+'.hdf5'
            ###Retrieve the parameters from the base file
            Param_Base = Retr().get_parameters(Basename)
            for i in Param_Base.keys():
                for j in Dico.keys():
                    ##if one parameter from the baseSSP is in the configuration
                    if i == j:
                        ##we check the list
                        color = CPB().check_input_vs_output(Dico, Param_Base[i], i, 80)[1]

                        ##if the color is right it is ok
                        if color == 'CURSOR':
                            Mandatory += 1
                        ##if not, we return an error message
                        else:
                            return 'No %s list given'%i, 'Incomplete'

        if Mandatory == 6:
            ##If everything is fine
            return 'Done', 'Done'

        elif Mandatory < 6:
            ##If something is missing
            return 'Incomplete', 'Incomplete'

    def check_datafile(self, Datafile, spec, phot, Nspec):
        """
        This function checks the datafile given by the user

        Parameters
        ---------
        Datafile    string, Path/to/the/file/and/file.dat

        Returns
        ------
        FILE        string, file.dat or error message
        DataMag     array of string, magnitude names
        """

        ##Check if a datafile (path+name) was given
        if len(Datafile) == 0:
            ##If not, print no Datafile in file name, and no magnitude array
            ##given
            FILE = 'No datafile'
            return FILE, []

        ##if something is given,extract path and filename
        PATH, FILE = os.path.split(Datafile)

        #Check a path was given and if it is on the system
        if len(PATH) == 0 or os.path.isdir(PATH) is False:
            ##if not, print 'Invalid name' and no magnitude array
            ## is given
            FILE = 'Invalid Path'
            return FILE, []
        else:
            #if a path is identified we give P='ok'
            P = 'ok'

        #Check filename and presence
        if len(FILE) == 0:
            ##if not, print 'Invalid name' and no magnitude array
            ## is given
            FILE = 'Invalid Name'
            return FILE, []
        else:
            #if a filename is identified we give F='ok'
            F = 'ok'

        if F == 'ok' and P == 'ok':
            ##If F=ok and P=ok we check if the datafile is there
            if os.path.isfile(Datafile) is False:
                ##if not, we pass 'File not found' as name
                ## and not magnitude array is given
                FILE = 'File Not Found'
                return FILE, []

            ###if we get here, we need to extract magnitude names 
            Magnames, message = Mags_list().extract(Datafile, spec, phot, Nspec)

            if message != 'ok':
                return message, []

            if message == 'ok':
                return FILE, Magnames



    def check_magfile_stru(self, magfile):
        """
        This function checks the structure of the magnitude conf
        file

        Parameter:
        ---------
        magfile     /path/and/file.mag

        Return      either the name of the file, or a error information
                    to be displayed
        ------
        """
        ##First we extract the name of the file
        MAGFILE = os.path.basename(magfile)
        try:
            ##Then we try to load the magfile
            Datamag = numpy.genfromtxt(magfile, dtype='str').T
        except:
            return 'Empty mag file', []

        ##Quick structure check (MUST be 6 column!)
        if len(Datamag) != 6:
            return 'Invalid Mag File', []

        if len(Datamag) == 6:
            ##If we detect the right structure
            magfromconf = []
            if Datamag.ndim == 1:
                ONE_FILT = {'name':'', 'Filter':'', 'Fit':'', 'Out':'', 'Abs':'', 'Nor':''}
                ONE_FILT['name'] = Datamag[0]
                ONE_FILT['Filter'] = Datamag[1]
                ONE_FILT['Fit'] = Datamag[2]
                ONE_FILT['Out'] = Datamag[3]
                ONE_FILT['Abs'] = Datamag[4]
                ONE_FILT['Nor'] = Datamag[5]
                magfromconf.append(ONE_FILT)

            elif Datamag.ndim == 2:
                for i in range(len(Datamag[0])):
                    ONE_FILT = {'name':'', 'Filter':'', 'Fit':'', 'Out':'', 'Abs':'', 'Nor':''}
                    ONE_FILT['name'] = Datamag[0][i]
                    ONE_FILT['Filter'] = Datamag[1][i]
                    ONE_FILT['Fit'] = Datamag[2][i]
                    ONE_FILT['Out'] = Datamag[3][i]
                    ONE_FILT['Abs'] = Datamag[4][i]
                    ONE_FILT['Nor'] = Datamag[5][i]
                    magfromconf.append(ONE_FILT)

        return MAGFILE, magfromconf

class check_main:
    """
    This class check the full configuration at once
    """

    def __init__(self, config_file):
        """
        Class Constructor, it takes the config file to check

        Parameters
        ----------
        Config_file  config file passed by the user

        """
        self.INPUT_CONF = read_config(config_file)

    def check_full(self):
        """
        This function checks the full configuration at once
        it goes along the CONF object and use the class 'check'

        For each section of the configuration file a message is
        displayed on the terminal to tell the user if the
        configuration is ok

        Parameter
        ---------
        None    we use self.config_file from the constructor

        Returns
        -------
        Return      OK/NOT OK
        """
        usespec = self.INPUT_CONF.CONF['UseSpec'].lower()
        usephot = self.INPUT_CONF.CONF['UsePhot'].lower()
        Mandatory = 0

        ###Check the general section
        General_status = check().check_General(self.INPUT_CONF.CONF)
        if General_status == 'Done':
            ##if it is ok, we tell the user it is
            MTU.Info('Section: General: OK\t ...Continue...', 'No')
            Mandatory += 1
        else:
            ###If not, we display the General status that
            ###returned an information
            MTU.Warning('Section: General: %s\t ...Continue...'%(General_status), 'No')

        ###Check the Fit section
        Fit_status = check().check_FIT(self.INPUT_CONF.FIT, usephot, usespec)
        if Fit_status in ['Done', 'Default']:
            ##if it is ok, we tell the user it is
            MTU.Info('Section: Fit: OK\t ...Continue...', 'No')
            Mandatory += 1
        else:
            ###If not, we display the Fit status that
            ###returned an information
            MTU.Warning('Section: Fit: %s\t ...Continue...'%(Fit_status), 'No')

        ###Check spectro if needed
        if usespec == 'yes':
            Spec_status = check().check_SPEC(self.INPUT_CONF.SPEC, self.INPUT_CONF.CONF['NSpec'])
            if Spec_status in ['Done']:
                ##if it is ok, we tell the user it is
                MTU.Info('Section: SPEC: OK\t ...Continue...', 'No')
                Mandatory += 1
            else:
                MTU.Warning('Section: SPEC: %s\t ...Continue...'%(Spec_status), 'No')


        else:
            MTU.Info('Section: No Spec used: OK\t ...Continue...', 'No')
            Mandatory += 1

        ###Check the Photo section
        Photo_status = check().check_PHOT(self.INPUT_CONF.PHOT)
        if Photo_status in ['Done']:
            ##if it is ok, we tell the user it is
            MTU.Info('Section: PHOT: OK\t ...Continue...', 'No')
            Mandatory += 1
        else:
            ###If not, we display the photo status that
            ###contained an information
            MTU.Warning('Section: PHOT: %s\t ...Continue...'%(Photo_status), 'No')

        ###check Library section
        if self.INPUT_CONF.LIB['Type'].lower() == 'provided':
            Lib_status = check().check_LibP(self.INPUT_CONF.LIB)[0]

        if self.INPUT_CONF.LIB['Type'].lower() == 'created':
            Lib_status = check().check_LibP(self.INPUT_CONF.LIB)[0]

        if self.INPUT_CONF.LIB['Type'].lower() == 'imported':
            Lib_status = check().check_LibP(self.INPUT_CONF.LIB)[0]

        if Lib_status == 'Done':
            ##if it is ok, we tell the user it is
            MTU.Info('Section: Library: OK\t ...Continue...', 'No')
            Mandatory += 1

        else:
            ###If not, we display the Cosmo status that
            ###returned an information
            MTU.Warning('Section Library: %s\t ...Continue...'%(Lib_status), 'No')


        ###Check the cosmo section
        Cosmo_status = check().check_COSMO(self.INPUT_CONF.COSMO)
        if Cosmo_status in ['Done', 'Default']:
            ##if it is ok, we tell the user it is
            MTU.Info('Section: COSMO: OK\t ...Continue...', 'No')
            Mandatory += 1
        else:
            ###If not, we display the Cosmo status that
            ###returned an information
            MTU.Warning('Section: Cosmo: %s\t ...Continue...'%(Cosmo_status), 'No')

        if Mandatory == 6:
            MTU.Info('Your configuration is OK\n', 'Yes')
            return 'ok', self.INPUT_CONF
        else:
            MTU.Warning('Your configuration is Incomplete\n', 'Yes')
            return 'no', []

