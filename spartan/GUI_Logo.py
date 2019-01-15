'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2018
#####
##### Logo for GUI display
#####
#####
############################
@License: GPL - see LICENCE.txt
'''
####Standard python library
import os

def icon():
    '''
    Method that return the logo of spartan to be displayed as icon
    for the GUI
    Returns:
    -------
    Log     list, of strings
    '''
    dir_path = os.path.dirname(os.path.realpath(__file__))
    logo_path = dir_path + '/GUI_styles' + '/rs.png'

    return logo_path


def Logo():
    '''
    methods that return the path to the main Logo of SPARTAN
    '''
    dir_path = os.path.dirname(os.path.realpath(__file__))
    logo_path = dir_path + '/GUI_styles'+'/SPARTAN_text_SPQR2.jpg'

    return logo_path

