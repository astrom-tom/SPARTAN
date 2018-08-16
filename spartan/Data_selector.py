'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####       2016-18
#####
#####   This file contains
#####   the code that organizes
#####   the data in *Lib.hdf5
#####        files
###########################
@License: GPL licence - see LICENCE.txt
'''

#### local imports
from . import Data_phot as phot
from . import Data_spec as spec
from . import Data_comb as comb


def data_selector(CONF):
    """
    This function determines what type of data file we have to make

    Parameter
    ---------
    CONF    Configuration from the input configuration file
    """
    status = 'nok'

    ####First case: Photometry alone
    if CONF.CONF['UseSpec'].lower() == 'no' and CONF.CONF['UsePhot'].lower() == 'yes':
        status = phot.file_phot(CONF)

    ####Second case: Spectroscopy alone
    if CONF.CONF['UseSpec'].lower() == 'yes' and CONF.CONF['UsePhot'].lower() == 'no':
        status = spec.file_spec(CONF)

    ####Third case: Combined fit
    if CONF.CONF['UseSpec'].lower() == 'yes' and CONF.CONF['UsePhot'].lower() == 'yes':
        status = comb.file_comb(CONF)

    return status
