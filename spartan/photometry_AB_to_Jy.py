'''
The SPARTAN Project
-------------------
conversion from AB to Jy and 
other way around
From
http://www.star.bristol.ac.uk/~mbt/stilts/sun256/uk.ac.starlink.ttools.func.Fluxes.html

@Author R. THOMAS
@year   2017
@place  UV/LAM/UCBJ/ESO
@License: GPL v3.0 licence - see LICENCE.txt
'''

##python libraries
import numpy

def AB_to_jy(AB, err, string):
    '''
    This function convert a magnitude in AB system
    to Jansky unit
    Parameters
    ----------
    AB      float, AB measurement
    err     err, error on the AB magnitude
    string  str, yes or no to output as string
    Return
    ------
    Jy      float, magnitude in Jansky
    Jerr    float, error on the magnitude in Jansky
    '''

    Jy = 1e23 * 10**(-(AB+48.6)/2.5) 
    Jyp =  1e23 * 10**(-(AB+err+48.6)/2.5) - Jy
    Jym = Jy-1e23 * 10**(-(AB+err+48.6)/2.5)
    if string == 'yes':
        return numpy.string(Jy), numpy.string_(numpy.mean((Jyp, Jym)))
    else:
        return Jy, numpy.mean((Jyp, Jym))



def Jy_to_AB(Jy, Jerr, string):
    '''
    This function convert a magnitude in Jy to AB system
    
    Parameters
    ----------
    Jy      float, Jy measurement
    Jerr     err, error on the Jy unit
    string  str, yes or no to output as string

    Return
    ------
    AB      float, magnitude in AB
    ABerr    float, error on the magnitude in AB
    '''

    AB = 2.5 * (23 - numpy.log10(Jy)) - 48.6 
    ABp = 2.5 * (23 - numpy.log10(Jy+Jerr)) - 48.6
    ABm = 2.5 * (23 - numpy.log10(Jy-Jerr)) - 48.6

    if string == 'yes':
        return numpy.string_(AB), numpy.string_(numpy.mean((ABp, ABm)))
    else:
        return AB, numpy.mean((ABp, ABm))
