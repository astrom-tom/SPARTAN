'''
The SPARTAN Project
-------------------
This file starts the TUI

@author: R. THOMAS
@year: 2016-2018
@place: UV/LAM/UCBJ/ESO
@License: GPL v3.0 - see LICENCE.txt

'''

##### Python standard Libraries
import os
###############################

##### local imports ###########
from . import messages as MTU
from . import config_file
from . import TUI_front
################################

def TUI(conf_file):
    """
    Class Constructor.

    Parameters:
    ----------
    Config_file     User provided config file or default SPARTAN
                    template

    return
    -------
    startfit        str, if we start the fit after the configuration (Yes or no)
    """
    ##first we read the config file
    INPUT_CONF = config_file.read_config(conf_file)

    #### Then we Get terminal size and check if we can display the TUI
    rows, columns = os.popen('stty size', 'r').read().split()

    ###smalles value = 30x80
    if int(rows) < 30 or int(columns) < 80:
        MTU.Error(\
                'Terminal size must be at least 80x30, \n\
                \t...Quitting SPARTAN TUI...\n', 'Yes')

        Startfit = 'No'

    ##if the terminal is big enough we can start the TUI
    else:
        ##Start the tui with the configuration
        TUIstart = TUI_front.Front(INPUT_CONF)
        TUIstart.run()
        ###Write the configuration file
        config_file.update_and_write_config(TUIstart.INPUT_CONF)
        ###Define start 
        Startfit = TUIstart.Startfit
    return Startfit
