#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
############################
#####
#####       SPARTAN
#####      R. THOMAS
#####        2018
#####
###########################
@License: GPL - see LICENCE.txt
'''

###import libraries
import sys
import os
from pathlib import Path
from subprocess import call
import socket

###Local modules
from .              import __info__ as info
from .              import command_line
from .              import messages as MTU
from .              import TUI_start as TUI
from .config_check  import check_main
from .Data_selector import data_selector
from .Lib_provided  import Compil_provided_LIB as CPL
from .              import fit_selector as fit
from .              import GUI_main as gui


def read_arg(args):
    """
    Read arguments passed to SPARTAN to check if at least 
    one argument (action) was passed

    Parameter
    --------
    args    obj, containing all the attributes from the cli
    """

    ##Check actions
    if args.tui in [None, False] and args.file in [None, False] and \
        args.check in [None, False] and args.run in [None, False] and \
        args.visua in [None, False] and args.OBJ in [None, False] and \
        args.docs in [False, None] and args.version in [None, False]:

        MTU.Error('You did not tell SPARTAN what to do,\n\
            ...SPARTAN --help or the documentation...\n\t\
        ...may help you....exit...\n', 'Yes')
        sys.exit()

def main():
    '''
    This is the main function of the code.
    if loads the command line interface and depending
    on the options specified by the user, start the 
    main window.
    '''

    ####first of all we check if the global configuration path is defined in the home directory 
    ##check if file exists
    home = str(Path.home())
    fileconf = os.path.join(home, '.spartan_conf')
    if not os.path.isfile(fileconf):
        #if we do not find it, we ask to create it
        path_conf = input('where are the input files located?, (give aboslute path)')
        with open(fileconf, 'w') as F:
            line0 = '#Path to input files\n'
            line = 'inputfile\t%s\n'%( path_conf)
            F.write(line0)
            F.write(line)

    ###then load the command line interface
    args = command_line.args()

    ####check if one argument is passed
    CheckArgs = read_arg(args)

    if args.version == True:
        MTU.Info('SPARTAN version %s'%info.__version__, 'No')
        sys.exit()

    if args.docs == True:
        ##check if there is any internet connection
        try:
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            url = info.__website__
        ##if not we use the local documentation distributed along the software
        except: 
            print('No internet connection detected, open local documentation')
            dir_path = os.path.dirname(os.path.realpath(__file__))
            url = os.path.join(dir_path, 'docs/build/html/index.html')

        for i in ['falkon', 'firefox', 'open', 'qupzilla', 'chromium', 'google-chrome']:
            ##we check if the command exist in the system
            exist = call(['which', i])
            if exist == 0:
                ##if it does then we use it to load the documentation
                call([i, url])
                ##and we stop the loop
                sys.exit()
                break
    
    ####open TUI
    if args.tui:
        try:
            if os.path.isfile(args.tui):
                Startfit = TUI.TUI(args.tui)

            else:
                ###Display error messages if file passed to tui is not found
                MTU.Error('The template file or the file you tried to pass,\n\
                    ...to the TUI was not found...\n\t\t\t...exit..\n', 'Yes')
                sys.exit()

            if Startfit == 'yes':
                ##first we check the file that was given
                statusconf, CONF = check_main(args.tui).check_full()
                #statusconf, CONF = check_config(args.file)
                if statusconf == 'ok':
                    ####We start to make datacube (or load it)
                    statusdatacube = data_selector(CONF)
                    ####Then start the library (or load it)
                    if statusdatacube == 'ok':
                        statusLIB = CPL().Load_config(CONF.LIB, CONF.CONF)
                        if statusLIB == 'Written':
                            fit.selector(CONF)

                    else:
                        MTU.Info('The datacube was not found/created', 'No')
                    
                else:
                    MTU.Error('You asked to run SPARTAN,\n\
                        ...But the configuration is incomplete...\n\t\t\t...exit..\n', 'No')
                    sys.exit()
        except KeyboardInterrupt:
            MTU.Info('Quitting SPARTAN...', 'Yes')

    #########check config
    if args.check:
        if args.file is None:
            ###Display error messages if input file is not provided
            MTU.Error('You asked to check your configuration of SPARTAN,\n\
            ...But did not provide a configuration file...\n\t\t\t...exit..\n', 'Yes')
            sys.exit()
        else:
            MTU.Info('Checking SPARTAN file: %s\n'%args.file, 'Yes')
            status = check_main(args.file).check_full()

    ##########run fit
    if args.run:
        try:
            if args.file is None:
                MTU.Error('You asked to run SPARTAN,\n\
                    ...But did not provide a configuration file...\n\t\t\t...exit..\n', 'Yes')
                sys.exit()

            else:
                ##first we check the file that was given
                statusconf, CONF = check_main(args.file).check_full()
                if statusconf == 'ok':
                    ####We start to make datacube (or load it)
                    statusdatacube = data_selector(CONF)
                    ####Then start the library (or load it)
                    if statusdatacube == 'ok':
                        statusLIB = CPL().Load_config(CONF.LIB, CONF.CONF)
                        if statusLIB == 'Written':
                            fit.selector(CONF)

                    else:
                        MTU.Info('The datacube was not found/created', 'No')
                    
                else:
                    MTU.Error('You asked to run SPARTAN,\n\
                        ...But the configuration is incomplete...\n\t\t\t...exit..\n', 'No')
                    sys.exit()

        except KeyboardInterrupt:
            MTU.Info('Quitting SPARTAN...', 'Yes')

    if args.visua:
        try:
            if args.file is None:
                MTU.Error('You asked to visualize SPARTAN results,\n\
                    ...But did not provide a configuration file...\n\t\t\t...exit..\n', 'Yes')
                sys.exit()

            else:
                ##first we check the file that was given
                statusconf, CONF = check_main(args.file).check_full()
                if statusconf == 'ok':
                    Resfile = os.path.join(CONF.CONF['PDir'],CONF.CONF['PName']+'_Res.hdf5')
                    if os.path.isfile(Resfile):
                        MTU.Info('Result file found, opening GUI', 'Yes')
                        MTU.Info('Load SPARTAN GUI with %s'%args.file, 'No')
                        gui.start_gui(CONF, Resfile)

                    else:
                        MTU.Error('Results file not found...exit...', 'Yes')
                else:
                    MTU.Error('You asked to visualize SPARTAN results,\n\
                        ...But the configuration is incomplete...\n\t\t\t...exit..\n', 'No')
                    sys.exit()

        except KeyboardInterrupt:
            MTU.Info('Quitting SPARTAN...', 'Yes')

    if args.OBJ:
        try:
            if args.file is None:
                MTU.Error('You asked to extract SPARTAN results,\n\
                    ...But did not provide a configuration file...\n\t\t\t...exit..\n', 'Yes')
                sys.exit()

            else:
                ##first we check the file that was given
                statusconf, CONF = check_main(args.file).check_full()
                if statusconf == 'ok':
                    MTU.Info('Extract SPARTAN result for object %s'%args.OBJ, 'No')
                else:
                    MTU.Error('You asked to extract SPARTAN results,\n\
                        ...But the configuration is incomplete...\n\t\t\t...exit..\n', 'No')
                    sys.exit()

        except KeyboardInterrupt:
            MTU.Info('Quitting SPARTAN...', 'Yes')




if __name__ == "__main__":
    main()
