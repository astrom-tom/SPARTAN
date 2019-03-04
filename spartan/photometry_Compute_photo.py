'''
The SPARTAN Project
-------------------
set of function dealing with photometry computation for the fit
in SPARTAN

@Author R. THOMAS
@year   2016-17
@place  UV/LAM/UCBJ/ESO
@License: GPL v3.0 licence - see LICENCE.txt
'''

####Python Standard Library
import warnings
import time
###########################

####Third Party############
import numpy
###########################

### Local imports#####################
from .units import Phys_const, length
######################################

warnings.filterwarnings("ignore")


def array_template_to_phot_init(Bands,Templates_hz, wave_at_z, freqTemp):
    '''
    Function that transform the template to magnitudes
    
    Parameters
    ----------
    Bands           list of dict, for each bands to compute
    Template_at_z,  NDarray, template library
    wave_at_z,      1Darray, of wavelength at z 
    Return
    ------
    F               NDarray, of shape (Nbands, Ntemplate) with the flux of 
                             Magnitudes
    '''
    ## We create an empty array of Nbands * Ntemplate
    ##for the fluxes 
    F = numpy.empty((len(Bands), len(Templates_hz)))
    ## and the magnitudes
    M = numpy.empty((len(Bands), len(Templates_hz)))
    t1 = time.time()
    m = 0
    for band in Bands:    
        ##retrieve filter information
        Lambda = band['Tran'][0]
        Tran = band['Tran'][1]
        Leff = band['Tran'][2]
        ##interpolate the filter throughput to the wavelength grid
        Trans_wave_model = numpy.interp(wave_at_z, Lambda, Tran)
        ## and normalise it
        Normalisation = numpy.trapz(Trans_wave_model, freqTemp[::-1]) 

        ###WARNING!!: [::-1] because for the integration of y=f(x), x must be increasing
        TranfreqNormed = Trans_wave_model / Normalisation
        ##I checked that numpy.trapz(TranfreqNormed[::-1], freqFilt[::-1])==1

        ##if we want to plot filters
        #c = length().m_to_ang(Phys_const().speed_of_light_ms())
        #plot().Filter_wave_hz(wave_at_z, Trans_wave_model, Leff, freqTemp, TranfreqNormed, c/Leff)
        #print(Lambda) 
        ####Make the ingration for each template
        #integration = numpy.trapz(Templates_hz*TranfreqNormed, freqTemp[::-1])
        integration = integ(Templates_hz, TranfreqNormed, freqTemp)
        ##and compute the magnitude for all of them at the same time
        if integration.size == 1 and integration[0]<0:
            M[m] =  -99.9
            F[m] =  -99.9
        else: 
            MagAB = -2.5*numpy.log10(integration)-48.60
            ##we save it in M
            M[m] = MagAB
            #And convert into flux
            Fluxes = mag2flux(MagAB, Leff)     
            ##and put it in F
            F[m] = Fluxes
            #next filter = next row in F
            m += 1
            
    return F, M

def integ(Templates_hz, TranfreqNormed, freqTemp):
    '''
    Method that makes the integration of the flux of the template inside the filter
    The first method was to integrate all the template at once using: 
        -->numpy.trapz(Templates_hz*TranfreqNormed, freqTemp[::-1])
    This took a little to much time. Therefore we cut the sample of template
    in chunks of 100 templates. And we integrate those chunks at once. It showed that
    it was almost 2 times faster.

    Parameter
    ---------
    Template_hz     numpy array, sample of template to integrate in frequency space
    TranfreqNormed  numpy array, Normalised filter in freq space
    freqTemp        numpy array, wavelength in frequency space


    Return
    ------
    integ           numpy array, of integration results
    '''
    
    A = Templates_hz*TranfreqNormed 
    if len(A) < 100:
        N = 10
    else:
        N = 100
    if len(A) > 10:
        a = [A[i:i + int(len(A)/N)] for i in range(0, len(A), int(len(A)/N))]
        integ = []
        for i in range(len(a)):
            integ.append(numpy.trapz(a[i], freqTemp[::-1]) )   
        integ = numpy.concatenate(integ)
    else:
        integ = numpy.trapz(A, freqTemp[::-1])

    return integ

def convert_wave_to_freq(wave, Templates):
    '''
    Function that converts an array of Template in erg/s/cm2/Ang to
                        an array of Template in erg/s/cm2/Hz

    To make this computation we follow
          lambda*F(lambda) = nu * F(nu)
          so F(nu) = (lambda/nu) * F(lambda)
    and since nu = c / lambda
       --> So we have F(nu) = (lambda^2 / c) * F(lambda)

    Note: It works also for individual templates
    ----
    Parameter
    ---------
    wave        1D array, wavelength of the template
    Templates   ND array, of template flux in erg/s/cm2/Ang

    Return
    ------
    Template_hz NDarray, of template flux in erg/s/cm2/Ang
    freq        1Darray, of freq from the wavelength
    '''

    ## so we retrieve the speed of light and convert it to Ang/s
    c = length().m_to_ang(Phys_const().speed_of_light_ms())
    ##and finally we convert the array
    Template_hz = Templates * (wave**2/c)
    
    ## and the wavelength
    freq = c / wave
    return freq, Template_hz


def mag2flux(mag, Leff):
    '''        
    Function that converts magnitude into flux in Ang
    Parameter
    ---------
    mag     float or list of float, of magnitude in AB system to compute
    Leff    float, effective wavelength of the filter

    Return
    ------
    flux_ang    float, corresponding flux in erg/s/cm2/Ang

    '''

    ##we convert the magniude (or array of magnitude). This gives a flux in 
    ## erg/s/cm2/Hz
    flux_hz = 10**((mag+48.6)/(-2.5))

    ## so we retrieve the speed of light and convert it to Ang/s
    c = length().m_to_ang(Phys_const().speed_of_light_ms())

    ## and then convert it into erg/s/cm2/ang
    flux_Ang = (c / Leff**2) * flux_hz 

    return flux_Ang
