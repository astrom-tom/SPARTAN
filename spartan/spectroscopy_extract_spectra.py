'''
The SPARTAN Project
-------------------
Extract ascii spectra from file

@Author R. THOMAS
@year   2017
@place  UV/LAM/UCBJ/ESO
@License: GPL v3.0 licence - see LICENCE.txt
'''

##python libraries
import numpy
import os


def extract_ascii_spectra(specnames, SpecDir):
    """
    This function extracts the spectra from the ascii file for
    a given object

    Parameters:
    ----------
    specnames  list, of spec names
    SpecDir    str, directory of the spectra
    CONF_spec  dict, spectroscopic configuration

    Returns:
    -------
    Final_Spec  numpy array,of three list with wave/Flux/err
    """

    asciifile = os.path.join(SpecDir, specnames)
    wave_table, spec_flux, spec_err = numpy.genfromtxt(asciifile).T

    ####
    SPEC = numpy.array([wave_table, spec_flux, spec_err])

    #we sort it, with respect to the lambda column (this should not be needed b
    #but we do it anyway)
    FINAL_Spec = numpy.array(sorted(SPEC.T, key=lambda x: x[0])).T

    return FINAL_Spec
