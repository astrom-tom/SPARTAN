'''

The SPARTAN Project 
-------------------
File: command_line.py

This file configures the Command line interface 

@author: R. THOMAS
@year: 2016-2018
@place: UV/LAM/UCBJ/ESO
@License: GPL v3.0 - see LICENCE.txt
'''

#### Python standard Libraries
import argparse

####SPARTAN Modules
from . import input_spartan_files


def args():
    """
    This function creates defines the 7 main arguments of SPARTAN using the argparse module
    """
    files = input_spartan_files.sp_input_files()

    parser = argparse.ArgumentParser(description="SPARTAN V1.0, R. Thomas, 2017, ESO,\n \
            This program comes with ABSOLUTELY NO WARRANTY; and is distributed under the GPLv3.0 Licence terms. \n\
            See the version of this Licence distributed along this code for details.")

    parser.add_argument("-f", "--file", \
            nargs='?',\
            const=None,\
            help="Configuration file. If no arg, the SPARTAN template will be taken")

    parser.add_argument("-t", "--tui", \
            nargs='?',\
            const=files.template_conf(),\
            help="start SPARTAN configuration TUI. \
                Default config file is the SPARTAN configuration template")

    parser.add_argument("-c", "--check",\
            action='store_true',\
            help="Check Configuration file, need a completed \
                configuration file from the -f command")

    parser.add_argument("-fo", "--OBJ",\
            nargs='?',\
            const=None,\
            help="Display on the terminal the informations about one \
                object in you data. Need a completed configuration \
                file from the -f command")

    parser.add_argument("-r", "--run", \
            action='store_true',\
            help="Start the fitting process, need a completed \
                configuration file from the -f command")

    parser.add_argument("-v", "--visua",\
            action='store_true',\
            help="Load the SPARTAN-GUI to visualize the results,need \
                a completed configuration file from the -f command ")

    parser.add_argument("-s", "--simu",\
            action='store_true',\
            help="Start simulation of galaxies. A complete simulation configuration \
                configuration file from the -f command ")

    parser.add_argument("--docs", action = "store_true", help="open the doc in web browser")
    parser.add_argument("--version", action = "store_true", help="display version of photon")

    ##### GET the Arguments for SPARTAN startup
    return parser.parse_args()
