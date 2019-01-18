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

####Python Standard Libraries###################################
import sys
import os
import time
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
################################################################

###Third party###
import numpy
import h5py
import tqdm
#################

###local imports#######################################
from . import messages as MTU
from . import photometry_AB_to_Jy as systemphot
from . import photometry_prepare_photo_fit as prepare
from . import spectroscopy_extract_spectra as ascii_spec
from . import photometry_Compute_photo as Comp_phot
#########################################################

def file_spec(CONF):
    """
    This function creates the datafle for photometry only
    Parameter:
    ----------
    CONF        dict, configuration of the user
    """
    
    ###initialize file names
    filenameDat = os.path.join(CONF.CONF['PDir'], '%s_dat.hdf5'%CONF.CONF['PName'])
    filenameRes = os.path.join(CONF.CONF['PDir'], '%s_Res.hdf5'%CONF.CONF['PName'])

    Nspec = int(CONF.CONF['NSpec'])
    SpecDir = CONF.SPEC['SDir']

    ###First we check if the datafile exists:
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

        #position of the first spectrum 
        N = 2

        ##### get the spectrum columns
        spec_cols = []
        c=0
        for i in range(Nspec):
            spec_cols.append(c+2)
            c+=3

        for i in tqdm.tqdm(range(len(ID))):
            #try:
                if Dat == 0:
                    ###then we create the list of magnitude
                    ###Each entry of the list is [magname, measure, error]
                    data_dico = []
                    if Magfile.ndim == 1:
                        if Magfile[2].lower() == 'yes':
                            mag_name = numpy.string_(Magfile[0])
                            if system == 'AB':
                                mag_meas = str(Cat[Nspec+2][i])
                                mag_err = str(Cat[Nspec+3][i])
            
                            else:
                                mag_meas, mag_err = systemphot.Jy_to_AB(Cat[Nspec+2][i], \
                                        Cat[Nspec+3][i], 'yes') 
                            ####nad save it
                            data_dico.append([mag_name, mag_meas, mag_err])

                    else:
                        for j,k in zip(range(len(Magfile)), range(len(spec_cols))):
                            if Magfile[j][2].lower() == 'yes':
                                mag_name = numpy.string_(Magfile[j][0])
                                if system == 'AB':
                                    mag_meas = Cat[spec_cols[k]+1][i]
                                    mag_err = Cat[spec_cols[k]+2][i]
                                else:
                                    mag_meas, mag_err = systemphot.Jy_to_AB(Cat[spec_cols[k]+1][i], \
                                            Cat[spec_cols[k]+2][i], 'yes')  

                                ####nad save it
                                data_dico.append([mag_name, mag_meas, mag_err])
                            
                    ###gather the names of spectrum files
                    spec_names = []
                    for k in spec_cols:
                        spec_names.append(Cat[k][i])

                    # we create the group
                    savedata = h5fdat.create_group(ID[i])

                    s = 1
                    #print(data_dico)
                    gal = indiv(ID[i])
                    for ll, jj in zip(spec_names, data_dico):
                        ###create object and get photo bands
                        #gal = indiv(CONF.PHOT['Photo_config'], ID[i], jj)
                        #print(jj[0], jj)
                        jj[0] = str(jj[0])[2:-1] 
                        gal.Magnitudes_spec = [jj]

                        ###extract data from the spectrum file
                        Final_spec = ascii_spec.extract_ascii_spectra(ll, SpecDir)
 
                        if float(jj[1]) < 0 :
                            gal.__dict__['Magnitudes_spec'][0][1] = 20
                            gal.__dict__['Magnitudes_spec'][0][2] = 20
                            prepare_data = prepare.Photo_for_fit(CONF.PHOT['Photo_config'], 0, 'spec')
                            prepare_data.match(gal)
                            freq, Specfreq = Comp_phot.convert_wave_to_freq(Final_spec[0], Final_spec[1])
                            F, M = Comp_phot.array_template_to_phot_init(prepare_data.allbands, \
                                    [Specfreq], Final_spec[0], freq)
                            gal.__dict__['Magnitudes_spec'][0][1] = M[0][0]
                            gal.__dict__['Magnitudes_spec'][0][2] = 4
                            MTU.Warning('For object %s: No valid magnitude was given for'%ID[i], 'No')
                            MTU.Warning('Spectro/Photo normalisation. SPARTAN computes a magnitude', 'No')
                            MTU.Warning('from the spectrum itself = %s +/- 4'%M[0][0],'No')
 
                        prepare_data = prepare.Photo_for_fit(CONF.PHOT['Photo_config'], 0, 'spec')
                        prepare_data.match(gal)
                        ###normalise the spectrum to the corresponding photometric point
                        freq, Specfreq = Comp_phot.convert_wave_to_freq(Final_spec[0], Final_spec[1])
                        ###compute the magnitude of the spectrum in the band given by the user
                        ### Final_spec[1] ==> [Final_spec[1]], the method takes array of template
                        ### as input
                        F, M = Comp_phot.array_template_to_phot_init(prepare_data.allbands, \
                                [Specfreq], Final_spec[0], freq) 
                        MagFlux = Comp_phot.mag2flux(float(jj[1]), prepare_data.allbands[0]['Tran'][2])
                        #---> compute the ratio F(phot)/F(spec) --> normalisation factor
                        #--> and apply it to the spectrum and to the error spectrum!
                        ratio = MagFlux/F[0][0]
                        Final_spec[1] = Final_spec[1]*ratio
                        Final_spec[2] = Final_spec[2]*ratio
                        '''
                        #####check we recompute the magnitude from the normalized spectrum
                        #####
                        freq, Specfreq = Comp_phot.convert_wave_to_freq(Final_spec[0], Final_spec[1])
                        F, M = Comp_phot.array_template_to_phot_init(prepare_data.allbands, [Specfreq], \
                                                Final_spec[0], freq)
                        print(ll, F, M, jj) #--> M must be equal to jj[1]
                        '''
                        savedata.create_dataset('spec%s'%s, data=Final_spec)
                        savedata.create_dataset('Mag%s'%s, data=numpy.array([jj]).astype(numpy.string_))
                        s+=1
                        

                    ##save_redshift
                    savedata.create_dataset('z', data=numpy.float(redshift[i]))

                if Res == 0:
                    ## we just create the groups
                    ##inside each ID group we create a subgroup 'General'
                    ##when we put 'NO' as fitting status
                    #try:
                    h5fRes.create_group(ID[i])
                    Fitted = h5fRes.create_group('%s/General'%ID[i])
                    Fitted.create_dataset('Fitted', data=numpy.string_('NO'))
                    #except:
                    #    MTU.Error('Could not create dataset in result file')
                    #    pass
            #except:
            #    MTU.Error('Could not create dataset in result file for %s'%ID[i], 'No')
            #    pass

        #then we close them
        if Res == 0:
            h5fRes.close()

        if Dat == 0:
            h5fdat.close()

        MTU.Info('Data file and result files created...Continue...', 'No')
        return 'ok'

class indiv:
    '''
    Thi class is used to make an object from a galaxy
    '''
    def __init__(self, ID):
        self.ID = ID
        self.Magnitudes_spec = ''
