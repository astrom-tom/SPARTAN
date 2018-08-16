'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
#####   This file contains
#####   the code that organizes
#####   *Lib.hdf5 for photometry
#####
###########################
@License: GPL licence - see LICENCE.txt
'''

####Python General Libraries##################################
import os
import time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
###############################################################

###Third party #########################
import numpy
import h5py
import tqdm
from astropy.io import fits as pyfits
########################################

###local imports###########################
from . import messages as MTU
from . import photometry_AB_to_Jy as systemphot
###########################################

def file_phot(CONF):
    """
    This function creates the datafle for photometry only
    Parameter:
    ----------
    CONF        dict, configuration of the user
    """

    filenameDat = os.path.join(CONF.CONF['PDir'], '%s_dat.hdf5'%CONF.CONF['PName'])
    filenameRes = os.path.join(CONF.CONF['PDir'], '%s_Res.hdf5'%CONF.CONF['PName'])

    ###First we check if the datafiles and result file exists:
    if os.path.isfile(filenameDat) is True:
        Dat = 1
    else:
        MTU.Info('Creating Data File ...Continue...', 'Yes')
        Dat = 0
        
    if os.path.isfile(filenameRes) is True:
        Res = 1
    else:
        MTU.Info('Creating Result File ...Continue...', 'No')
        Res = 0

    if Res == 1 and Dat == 1:
        #Everything is ready
        MTU.Info('Data file and Result file already exists...Continue...', 'No')
        return 'ok'

    ###Datafile preparation
    if Dat == 0:
        h5fdat = h5py.File(filenameDat, 'w')

    if Res == 0:
        h5fRes = h5py.File(filenameRes, 'w')

    if Dat != 1 or Res != 1:
        ### Then we open the catalog and magfile,
        #and load the photometric configuration

        Cat = numpy.genfromtxt(CONF.CONF['PCat'], dtype='str').T
        #Mags = CONF.PHOT['Photo_config']
        Magfile = numpy.genfromtxt(CONF.PHOT['Photo_file'], dtype='str')
        system = CONF.PHOT['System']
        ###Load the 2 first columns
        ID = Cat[0]
        redshift = Cat[1].astype('float')
        ###For photommetry only, the magnitude columns start
        ###at N=2. N=0: ID;  N=1: z
        N = 2
        for i in tqdm.tqdm(range(len(ID))):
             try:
                if Dat == 0:
                    ##First we create the group
                    data = h5fdat.create_group(ID[i])
                    ###then we create the list of magnitude
                    ###Each entry of the list is [magname, measure, error]
                    data_dico = []
                    for j in range(len(Magfile)):
                        if Magfile[j][2].lower() == 'yes':
                            mag_name = numpy.string_(Magfile[j][0])
                            if system == 'AB':
                                mag_meas = numpy.string_(Cat[N+j*2][i])
                                mag_err = numpy.string_(Cat[N+j*2+1][i])
                            if system == 'Jy':
                                mag_meas, mag_err = systemphot.Jy_to_AB(Cat[N+j*2][i], Cat[N+j*2+1][i], 'yes')
                            data_dico.append([mag_name, mag_meas, mag_err])

                    ##Then we put data_dico as a dataset in the ID group
                    data.create_dataset('Mag', data=data_dico)
                    ##redshift dataset. WARNING: Here scalar dataset!
                    data.create_dataset('z', data=numpy.float(redshift[i]))
                if Res == 0:
                    ## we just create the groups
                    ##inside each ID group we create a subgroup 'General'
                    ##when we put 'NO' as fitting status
                    try:
                        h5fRes.create_group(ID[i])
                        Fitted = h5fRes.create_group('%s/General'%ID[i])
                        Fitted.create_dataset('Fitted', data=numpy.string_('NO'))
                    except:
                        pass
             except:
                MTU.Error('Could not create dataset in result file for %s'%ID[i], 'No')
                pass

        #then we close them
        if Res == 0:
            h5fRes.close()

        if Dat == 0:
            h5fdat.close()

        MTU.Info('Data file and result files created...Continue...', 'No')
        return 'ok'

