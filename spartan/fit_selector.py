'''
The SPARTAN project
-------------------
This short module select the right fit to do from the user informations

@author: R. THOMAS
@year: 2017
@place: UV/LAM/UCBJ/ESO
@License: GPL licence - see LICENCE.txt
'''
##SPARTAN Modules
from .             import messages as MTU
from .fit_photo    import Fit_photo
from .fit_spectro  import Fit_spectro
from .fit_combined import Fit_combined
#----------------------------------------------------------

def selector(config):
    '''
    This method looks at the USER configuration and
    select the right fit to use

    Parameter:
    ---------
    config  dict, configuration of the user

    Return:
    ------
    Fit_end str, end fit status
    '''
    ##1- we first have to check what kind of data the user wants to fit
    if config.CONF['UsePhot'].lower() == 'yes'\
            and config.CONF['UseSpec'].lower() == 'no':

        MTU.Info('Start the fit on the PHOTOMETRY only', 'Yes')
        Init = Fit_photo(config) 
        Init.main()

    if config.CONF['UsePhot'].lower() == 'no' \
            and config.CONF['UseSpec'].lower() == 'yes':

        MTU.Info('Start the fit on the SPECTROSCOPY only', 'Yes')
        Init = Fit_spectro(config)
        Init.main()

    if config.CONF['UsePhot'].lower() == 'yes' \
            and config.CONF['UseSpec'].lower() == 'yes':


        MTU.Info('Soon to be released', 'Yes')
        Init = Fit_combined(config)
        #Init.main()
