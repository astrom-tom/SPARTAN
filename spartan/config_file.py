'''
The SPARTAN Project
-------------------
This file read the configuration files

@author: R. THOMAS
@year: 2016-2018
@place: UV/LAM/UCBJ/ESO
@License: GPL v3.0 - see LICENCE.txt
'''

##### Python Libraries
import os
import sys
import configparser
from shutil import copyfile

##Third party
import numpy

##### Local imports
from . import messages as MTU
from .input_spartan_files import sp_input_files as PIF


class read_config:
    """
    This class extract information from config file

    Attributes:
    ----------
        self.CONF   Python Dictionnary containing the general
                    configuration informations
        self.SPEC   Python Dictionnary containing the Spectroscopic
                    configuration informations
        self.Photo  Python Dictionnary containing the Photometric
                    configuration informations
        self.LIB    Python Dictionnary containing the Library
                    configuration informations
        self.COSMO  Python Dictionnary containing the cosmological model
                    configuration informations
        self.FIT    Python Dictionnary containing the fitting procedure
                    configuration informations
    """
    def __init__(self, config_file):
        """
        Class Constructor
        """
        config = configparser.ConfigParser()
        config.read(config_file)

        #####General informations
        CONF = {'PName':'', 'AName':'', 'PDir':'', 'NCPU'\
                :'', 'PCat':'', 'UsePhot':'', 'UseSpec':'', 'NSpec':'', \
                'TryZ':''}

        CONF['PName'] = config.get('General', 'Project_name')
        CONF['AName'] = config.get('General', 'Author')
        CONF['PDir'] = config.get('General', 'Project_Directory')
        CONF['NCPU'] = config.get('General', 'NCPU')
        CONF['PCat'] = config.get('General', 'Data_cat')
        CONF['UsePhot'] = config.get('General', 'Use_Phot')
        CONF['UseSpec'] = config.get('General', 'Use_Spec')
        CONF['NSpec'] = config.get('General', 'NSpec')
        self.CONF = CONF


        ######SPECTROSCOPIC informations
        SPEC = {'SDir':'', 'UseFS':'', 'Binning':'', 'SpecZ':'', 'Funit'\
                :'', 'Wunit':'', 'Skip':'', 'SSkip':'', 'UseBR':'', 'BR'\
                :''}

        SPEC['SDir'] = config.get('Spectroscopy', 'Spectra_Directory')
        SPEC['Res'] = config.get('Spectroscopy', 'Resolution')
        SPEC['Funit'] = [config.get('Spectroscopy', 'Flux_Units')]
        SPEC['Wunit'] = [config.get('Spectroscopy', 'Wave_Units')]
        SPEC['Skip'] = config.get('Spectroscopy', 'Skip_edges').lower()
        SPEC['SSkip'] = config.get('Spectroscopy', 'Size_Skipped')
        SPEC['UseBR'] = config.get('Spectroscopy', 'Bad_Regions').lower()
        SPEC['BR'] = config.get('Spectroscopy', 'BAD_Regions_list')
        SPEC['Norm'] = config.get('Spectroscopy', 'Normalisation_type').lower()
        SPEC['Norm_reg'] = config.get('Spectroscopy', 'Norm_region')
        SPEC['Calib'] = config.get('Spectroscopy', 'Multi_spec_calibration').lower()

        self.SPEC = SPEC

        ####LIBRARY information
        LIB = {'Type':'', 'Base':''}

        LIB['Type'] = config.get('Library', 'Type').lower()
        LIB['BaseSSP'] = config.get('Library', 'BaseSSP')
        LIB['DustUse'] = config.get('Library', 'DustUse').lower()
        LIB['EBVList'] = config.get('Library', 'EBVList')
        LIB['IGMtype'] = config.get('Library', 'IGMType').lower()
        LIB['EMline'] = config.get('Library', 'EMline').lower()
        LIB['Emline_skipped'] = config.get('Library', 'EMline_skipped')
        LIB['Age'] = config.get('Library', 'Age')
        LIB['TAU'] = config.get('Library', 'TAU')
        LIB['MET'] = config.get('Library', 'MET')
        self.LIB = LIB

        #### COSMOLOGICAL Model configuration
        COSMO = {'Ho':'', 'Omega_L':'', 'Omega_m':'', 'UseCo':''}

        COSMO['Ho'] = config.get('Cosmo', 'Ho')
        COSMO['Omega_L'] = config.get('Cosmo', 'Omega_L')
        COSMO['Omega_m'] = config.get('Cosmo', 'Omega_m')
        COSMO['UseCo'] = config.get('Cosmo', 'Use_Cosmo')
        self.COSMO = COSMO

        #### FITTING configuration
        FIT = {'Algo':'', 'OverFit':'', 'PDFV'\
                :'', 'BFV':'', 'KeepPDF':'', 'Combined':''}

        FIT['Algo'] = config.get('Fit', 'Algorithm')
        FIT['OverFit'] = config.get('Fit', 'OverFit')
        FIT['PDFV'] = config.get('Fit', 'PDF_values')
        FIT['BFV'] = config.get('Fit', 'Best_Fit_Values')
        FIT['KeepPDF'] = config.get('Fit', 'Keep_Full_PDF')
        FIT['Combined'] = config.get('Fit', 'Combined')
        self.FIT = FIT

        #### Photo configuration
        PHOT = {'DataFile':'', 'PhotoConf':'', 'System':'', 'Spec':'',\
                'Phot':'', 'Nspec':'', 'Photo_config':''}

        PHOT['DataFile'] = config.get('General', 'Data_cat')
        PHOT['Photo_file'] = config.get('Photo', 'Photofile')
        #read the magfile
        MAGFILE, photo_config = Magfile().Read(PHOT['Photo_file'])
        PHOT['Photo_config'] = photo_config
        PHOT['System'] = config.get('Photo', 'System')
        PHOT['Phot'] = config.get('General', 'Use_Phot')
        PHOT['Spec'] = config.get('General', 'Use_Spec')
        PHOT['NSpec'] = config.get('General', 'NSpec')
        del MAGFILE
        self.PHOT = PHOT

class update_and_write_config:
    """
    This class writes or update on the disc the config file from the configuration
    completed from the TUI
    """
    def __init__(self, CONF):
        """
        Class Constructor.
        We check here 2 things: The presence of the project directory
                                and the presence of the Project file

        Parameter
        ---------
        CONF        Object that has, as attributes, all the dictionnaries
                    of the configuration

        Return
        ------
        """

        ###First we check if a directory is passed
        PDir = CONF.CONF['PDir']
        if PDir == '':
            ##if no directory was given, we can not write down the config
            ##SPARTAN error-->exit
            MTU.Error(\
                    'You did not give a Project Directory,\n\
                    ...SPARTAN can not write down the conf file...\n\t\
                    ...exit..\n'
                    , 'Yes')
            sys.exit()

        elif os.path.isdir(PDir):
            ##The directory already exists
            MTU.Info(\
                    'Project Directory already exists...Continue...'
                    , 'No')
        else:
            ##If we reach this place we need to create the directory
            ##We try...
            try:
                ##to create the directory
                os.makedirs(PDir)
                MTU.Info(\
                        'Create Project Directory...Continue...'
                        , 'No')
            except:
                ##If it fails, we exit and tell the user we could
                ## not create it
                MTU.Error(\
                        'Can not create Project Directory...\n\
                        ...exit...\n'
                        , 'Yes')

                sys.exit()

        ##Then we check if the config file exists
        ##The config file is Project/Dir/Project_name.conf
        config_file = os.path.join(PDir, '%s.conf'%CONF.CONF['PName'])
        ##checking
        if os.path.isfile(config_file):
            MTU.Info('Project file already exists...'+\
                            '...Check for update...Continue...'\
                            , 'No')
            ## if the projectfile already exist we go to see if we
            ## have to update it

            self.write_configuration_file(config_file, CONF, 'old')

        else:
            MTU.Info('Create Project file...Continue...'\
                        , 'No')
            ##if the projectfile does not exist we have to create
            ##and fill it
            self.write_configuration_file(config_file, CONF, 'new')


    def write_configuration_file(self, config_file, CONF, status):
        """
        This function write (create or update) the configuration
        file from either the template file given with the SPARTAN
        installation or the old template given by the user

        Parameters:
        ----------
        configfile  /path/to/config/file.conf
        CONF        CONF from TUI or user file
        status      if it is a new file to create or an old one to update

        Returns:
        --------
        """

        ##Extract Empty configuration file
        Template_conf = PIF().template_conf()

        if status == 'new':

            ###If we create a new oine from scratch we have to
            ###copy the template.cfg to the project directory
            try:
                copyfile(Template_conf, config_file)
                MTU.Info('Project file Created...Continue...'\
                                , 'No')
            except:
                ##if the creation does not work, we quit
                MTU.Error('Can not create Project file...'+\
                                '...exit...\n'\
                                , 'Yes')
                ##and exit
                sys.exit()

        elif status == 'old':
            ##if we take an old one we don't need to do anything
            ##for the moment
            pass

        ##From here we write the config file
        config = configparser.ConfigParser()
        config.read(config_file)

        ##Create the general configuration
        config.set('General', 'Project_name', CONF.CONF['PName'])
        config.set('General', 'Author', CONF.CONF['AName'])
        config.set('General', 'Project_Directory', CONF.CONF['PDir'])
        config.set('General', 'NCPU', CONF.CONF['NCPU'])
        config.set('General', 'Data_cat', CONF.CONF['PCat'])
        config.set('General', 'Use_Phot', CONF.CONF['UsePhot'])
        config.set('General', 'Use_Spec', CONF.CONF['UseSpec'])
        config.set('General', 'NSpec', CONF.CONF['NSpec'])

        ###Create the Cosmological configuration
        config.set('Cosmo', 'Ho', CONF.COSMO['Ho'])
        config.set('Cosmo', 'Omega_L', CONF.COSMO['Omega_L'])
        config.set('Cosmo', 'Omega_m', CONF.COSMO['Omega_m'])
        config.set('Cosmo', 'Use_Cosmo', CONF.COSMO['UseCo'])

        ###create the Lib section
        config.set('Library', 'Type', CONF.LIB['Type'])
        config.set('Library', 'BaseSSP', CONF.LIB['BaseSSP'])
        config.set('Library', 'DustUse', CONF.LIB['DustUse'])
        config.set('Library', 'EBVList', CONF.LIB['EBVList'])
        config.set('Library', 'IGMtype', CONF.LIB['IGMtype'])
        config.set('Library', 'EMline', CONF.LIB['EMline'])
        config.set('Library', 'EMline_skipped', CONF.LIB['Emline_skipped'])
        config.set('Library', 'MET', CONF.LIB['MET'])
        config.set('Library', 'TAU', CONF.LIB['TAU'])
        config.set('Library', 'Age', CONF.LIB['Age'])

        ###Create the photometry configuration
        ##Magfile
        photfile = os.path.join(CONF.CONF['PDir'], '%s.mag'% CONF.CONF['PName'])
        config.set('Photo', 'Photofile', photfile)
        config.set('Photo', 'System', CONF.PHOT['System'])

        ###Create the Spectroscopic configuration section
        config.set('Spectroscopy', 'Spectra_Directory', CONF.SPEC['SDir'])
        config.set('Spectroscopy', 'resolution', CONF.SPEC['Res'])
        try:
            config.set('Spectroscopy', 'Flux_Units', CONF.SPEC['Funit'][0])
        except:
            config.set('Spectroscopy', 'Flux_Units', '')
        try:
            config.set('Spectroscopy', 'Wave_Units', CONF.SPEC['Wunit'][0])
        except:
            config.set('Spectroscopy', 'Wave_Units', '')
        config.set('Spectroscopy', 'Skip_edges', CONF.SPEC['Skip'])
        config.set('Spectroscopy', 'Size_Skipped', CONF.SPEC['SSkip'])
        config.set('Spectroscopy', 'Bad_Regions', CONF.SPEC['UseBR'])
        config.set('Spectroscopy', 'BAD_Regions_list', CONF.SPEC['BR'])
        config.set('Spectroscopy', 'Normalisation_type', CONF.SPEC['Norm'])
        config.set('Spectroscopy', 'Norm_region', CONF.SPEC['Norm_reg'])
        config.set('Spectroscopy', 'Multi_spec_calibration', CONF.SPEC['Calib'])



        ###Create the Fit configuration section
        config.set('Fit', 'Algorithm', CONF.FIT['Algo'])
        config.set('Fit', 'OverFit', CONF.FIT['OverFit'])
        config.set('Fit', 'PDF_values', CONF.FIT['PDFV'])
        config.set('Fit', 'Best_Fit_Values', CONF.FIT['BFV'])
        config.set('Fit', 'Keep_Full_PDF', CONF.FIT['KeepPDF'])
        config.set('Fit', 'Combined', CONF.FIT['Combined'])

        with open(config_file, 'w') as myconfig:
            config.write(myconfig)

        MTU.Info('Project file ended...Continue...', 'No')

        ##We write the Magfile here
        if os.path.isfile(photfile):
            MTU.Info('Magfile already exists...'+\
                            '...Check for update...Continue...'\
                            , 'No')
            ## magfile already exist we go to see if we
            ## have to update it
            status_Magfile = Magfile().Write(CONF.PHOT['Photo_config'], photfile)
            if status_Magfile == 'ok':
                MTU.Info('Magfile Updated...Continue', 'No')

            else:
                MTU.Warning('Could not update Magfile', 'No')

        else:
            MTU.Info('Create Magfile...Continue...', 'No')
            ##if magfile does not exist we have to create
            ##and fill it
            status_Magfile = Magfile().Write(CONF.PHOT['Photo_config'], photfile)

            if status_Magfile == 'ok':
                MTU.Info('Magfile Created...Continue', 'No')

            else:
                MTU.Warning('Could not create Magfile', 'No')


class Magfile:
    """
    This class deals with the magnitude file
    2 methods are implemented:
    Read_file and Write_file
    """
    def __init__(self,):
        """
        Class Constructor, empty for the moment
        """
        pass

    def Write(self, Photo_config, MagfileName):
        """
        Function that creates the Magnitude file configuration

        Paramters:
        ---------
        Photo_conf  Photometric configuration
        MagfileName Path/and/magfile.mag

        Returns:
        -------
        status      ok or not ok

        """
        try:
            with open(MagfileName, 'w') as magconfig:
                ##First we write the header:
                magconfig.write('#Mag\tFilter\tFit\tOut\tAbs\tNorm\n')
                ##From each filter we extract the configuration
                for i in Photo_config:
                    line = '%s\t%s\t%s\t%s\t%s\t%s\n'\
                    %(i['name'], i['Filter'], i['Fit'], i['Out'], i['Abs'], i['Nor'])
                    magconfig.write(line)
            return 'ok'

        except:
            return 'Not ok'

    def Read(self, magfile):
        """
        Function that reads the magfile passed into the config file

        Parameter
        ---------
        magfile     path/and/file.mag

        Return
        ------
        magfromconf list of filter dictionnaries
        """
        ##First we retrieve the name of the file
        MAGFILE = os.path.basename(magfile)

        try:
            ##Then we try to load the magfile
            Datamag = numpy.genfromtxt(magfile, dtype='str').T
        except:
            return 'Empty mag file', []
        ##Quick structure check
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
