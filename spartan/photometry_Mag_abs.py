'''
The SPARTAN Project
-------------------
Modul dealing with the absolute magnitude computation
in SPARTAN

@Author R. THOMAS
@year   2016-18
@place  UV/LAM/UCBJ/ESO
@License: GPL v3.0 licence - see LICENCE.txt
'''

####Python Standard Libraries
import scipy
#############################

### Local imports############################################################
from .                    import photometry_Compute_photo as Compute_photo
from .photometry_filters  import Retrieve_Filter_inf
from .units               import Phys_const, length
###############################################################################

def main(Template, photo_conf, Redshift, COSMO):
    '''
    This method is the main of the magnitude absolute estimation.
    The method is the following. We deredshift the template and put
    it at 10pc. Then we compute the apparent magnitude of this
    de-redshifted template --> Absolute Magnitude
    '''
    ### first we extract wave and flux from the template
    wave, flux = Template

    ### then we deredshift it
    wavenoz, fluxnoz = deredshift(wave, flux, Redshift, COSMO)

    ## then we put it at 10pc
    flux_10pc = to10pc(fluxnoz) 

    ##retrieve magnitude names for absolute magnitude
    magabs_name = []
    for j in photo_conf:
        ##if the user asked for the absolute magnitude
        if j['Abs'] == 'yes':
            magabs_name.append(j['Filter'])


    #convert template to frequence space
    freq, freqTemp = Compute_photo.convert_wave_to_freq(wavenoz, flux_10pc)

    magabs_L = []
    bands = []
    ##and compute magnitude
    for i in magabs_name:
        Tran = Retrieve_Filter_inf().retrieve_one_filter(i)
        ###save the wwavelength
        magabs_L.append(Tran[2])
        b = {}
        b['Tran'] = Tran
        bands.append(b)

    F, M = Compute_photo.array_template_to_phot_init(bands, [freqTemp], wavenoz, freq)
    Magabs = {}
    Magabs['Name'] = magabs_name
    Magabs['Wave'] = magabs_L
    Magabs['Meas'] = [i[0] for i in M]

    return Magabs


def to10pc(fluxnoz):
    '''
    This methods take a restframe template and put it at 10pc
    Parameter
    ---------
    Wavenoz     list, of restframe wavelength
    fluxnoz     list, of restframe flux

    Return
    ------
    wave10pc    list, of restframe wavelength
    flux10pc    list, of flux at 10pc

    '''
    ###first we compute the distance in cm
    dlim10pc=length().pc_to_cm(10.) #pc to cm

    ##and put the flux at 10 pc:
    flux_10pc=fluxnoz/(4*scipy.constants.pi*dlim10pc**2)

    return flux_10pc
    

def deredshift(wave, flux, z, COSMO):
    '''
    This method takes as input a redshifted and normed template
    and de-redshift it
    Parameter
    ---------
    wave    list, of wavelength of the template
    flux    list, of flux of the wavelength
    z       float, redshift of the template
    COSMOS  dict, Cosmology at z

    Return
    ------
    wavenoz list, of deredshifted template
    fluxnoz list, of deredshifted flux
    '''

    wavenoz = wave / (1+z)
    fluxnoz = flux * (1+z)*4*scipy.constants.pi*(COSMO['DL']**2) 

    return wavenoz, fluxnoz
