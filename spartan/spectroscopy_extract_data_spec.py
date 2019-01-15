'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016-18
#####
#####   This file contains
##### the code that extract
#####  and get the normalisation
#####   for the spec fit
###########################
@License: GPL licence - see LICENCE.txt
'''

##Third party libraries
import numpy
######################3

##local imports#############
from .photometry_filters import Retrieve_Filter_inf
from .                   import photometry_Compute_photo as Comp_phot
##############################

def extract_datasets(datasets, obj, CONF, redshift):
    '''
    This methods extract the datasets from the
    hdf5 datafile
    Parameters
    ----------
    datasets    list, of dataset in the group
    obj         hdf5 group, corresponfing to the object
    CONF        dict, CONF by the user
    '''
 
    ##create empty array
    Mags = []
    specs = []
    data = {}
    Norm = []
    Norm_calin = [] 
    ###estimate the number of spectra (-1 because)
    ##there is the redshift
    if CONF.CONF['UseSpec'].lower() == 'yes' and CONF.CONF['UsePhot'].lower() == 'yes':
        Nspec = (len(datasets)-2)/2

    else:
        Nspec = (len(datasets)-1)/2

    ###We check if the number of spectrum
    ###from the datafile is indeed equal to NSpec
    ###given by the user (double check with datafile)
    ###maker. (Better more checks then no checks :) )

    if Nspec!=float(CONF.CONF['NSpec']):
        return 'NO', data, Norm
    
    ###create keys in the dictionnary
    for i in range(int(Nspec)):
        data[i+1] = []

    ###extract Photo config
    photo_conf = CONF.PHOT['Photo_config']

    ###we loop over the dictionnary of data
    for i in data:
        ##and initialize the values
        name = ''
        Meas = -99.9
        errm = -99.9
        wave = []
        flux = []
        errf = []
        weight = []
        ##then we look in the dataset
        ##and fill the values with
        ##real values
        for j in datasets:
            if j[0:-1] == 'spec' and int(j[-1]) == i:
                wavespec = numpy.array(obj[j][0])
                fluxspec = numpy.array(obj[j][1])
                errfspec  = numpy.array(obj[j][2])
                ###look for places where the errors are null
                indexs = numpy.where(errfspec != 0) 
                ###and consider only these ones for the spectrum
                wavespec = wavespec[indexs]
                fluxspec = fluxspec[indexs]
                errfspec = errfspec[indexs]


        for j in datasets:
            if j[0:-1] == 'Mag' and int(j[-1]) == i:
                ###find if we normalize
                for k in photo_conf:
                    if k['name'] == str(obj[j][0][0])[2:-1]:
                        if k['Nor'] == 'yes':
                            Nor = 'yes'
                        else:
                            Nor = 'no'
                        break

                ##then what kind of nromalisation (region or mags)
                if CONF.SPEC['Norm'] == 'mags':
                    name = str(obj[j][0][0])
                    Meas = float(obj[j][0][1])
                    errm =  float(obj[j][0][2])

                else:
                    ##extract region file
                    if float(CONF.CONF['NSpec']) == 1:
                        wave_reg = numpy.array(CONF.SPEC['Norm_reg'].split('-')).astype('float')
                        name, Meas, errm = emission_line_free(obj[j], wave_reg, \
                                wavespec, fluxspec, redshift)

                        ####if we got a problem with the spectral-magnitude estimation
                        ####we come back to the magnitude normalisation
                        if Meas < 0.0:
                            name = str(obj[j][0][0])
                            Meas = float(obj[j][0][1])
                            errm =  float(obj[j][0][2])

                    else:
                        regions = numpy.array(CONF.SPEC['Norm_reg'].split(';')[i-1].split('-')).astype('float')
                        name, Meas, errm = emission_line_free(obj[j], regions, wavespec, fluxspec,\
                                redshift)
                        if Meas < 0.0:
                            name = str(obj[j][0][0])
                            Meas = float(obj[j][0][1])
                            errm =  float(obj[j][0][2])

        ##finally save into the dictionnary
        data[i] = [name, Meas, errm, wavespec, fluxspec, errfspec, Nor]    

    ###we choose the first band for normalization of templates
    for i in data:
        if data[i][-1] == 'yes':
            Norm.append(data[i][0:3])

    return data, Norm


def emission_line_free(obj, wave_reg, wave, flux, redshift):
    '''
    This method looks for an emission line free regions
    in the spectrum and create a door-filter to compute 
    the observed magnitude in it
    Parameters:
    ---------
    obj         dict, of the observation object we are considering
    wave_reg    array, of the door filter
    wave        array, of spec wavelength
    flux        array, of spec flux

    Return:
    -------
    name       str,     name of the filter
    Meas       float,   measure of the error
    err        err,     measure of the error
    '''
    
    if redshift > 0 :
        ##and create rectangular filter
        band = Retrieve_Filter_inf().rectangular(wave_reg[0]*(1+redshift),\
                wave_reg[1]*(1+redshift))

        ###then we must compute the magnitude of the template in this
        ###region
        freq, Specfreq = Comp_phot.convert_wave_to_freq(wave, flux)    
        F, M = Comp_phot.array_template_to_phot_init([band], [Specfreq], \
                                                wave, freq) 

        ###check with plot
        #plot().spec_porte(wave, flux, [band['Tran'][2]], F[0],\
        #       self.redshift, rectangular_limit)

        name = ['door', wave_reg[0]*(1+redshift), wave_reg[1]*(1+redshift)]
        Meas = M[0][0]
        errm = float(obj[0][2])

    else:
        name = str(obj[0])
        Meas = float(obj[1])
        errm =  float(obj[2])

    return name, Meas, errm 
