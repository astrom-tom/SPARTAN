'''
The SPARTAN Project
-------------------
This file configures the messages passed to the user


@author: R. THOMAS
@year: 2016-2018
@place: UV/LAM/UCBJ/ESO
@License: GPL v3.0 - see LICENCE.txt
'''


####Python Libs
import os


def Logo():
    '''
    Method that return the logo of spartan to be displayed in the
    terminal
    Returns:
    -------
    Log     list, of strings
    '''

    logo1 = """____  ____       ____  _____       __   _"""
    logo2 = """/ ___||  _ \ /\  |  _ \|_   _| /\  |  \ | |"""
    logo3 = """\___ \| |_) / _\ | |_) | | |  / _\ |   \| |"""
    logo4 = """ ___) |  __/ __ \|  _ <  | | / __ \| |\   |"""
    logo5 = """|____/|_| /_/  \_\_| \_| |_ /_/  \_\_| \__|"""
    logo6 = """R.THOMAS\t\t\t\t\t\t\t\t\t\t\t@UV/LAM \t\t\t\t\t\t\t\t\t\t\t\t2017"""
    log = [logo1, logo2, logo3, logo4, logo5, logo6, '']

    return log


def welcome_mess():
    '''
    methods that return the welcome message of SPARTAN
    '''
    wel = ['', 'To start configuring a new run please hit each',\
        'following configuration section. Once you have',\
        'all the green lights you can hit the OK button',\
        'to exit the configuration.  Enjoy!!! :)   ']

    return wel

def Error(message, toline):
    """
    This function display an error message. After such a message
    SpArtan must quit

    Paramters:
    ---------
    message:    str,Message to be displayed
    toline:     str,Carriage return or not before the message(Yes or No)

    Returns:
    -------

    """
    if toline == 'Yes':
        print('\n'+ '\033[1m' + '[ERROR]:\t' + message + '\033[0m')
    else:
        print('\033[1m' + '[ERROR]:\t' + message + '\033[0m')

def Warning(message, toline):
    """
    This function display an warning message.
    This message does not lead to the end of SPARTAN

    Paramters:
    ---------
    message:    str,Message to be displayed
    toline:     str,Carriage return or not before the message(Yes or No)

    Returns:
    -------

    """

    if toline == 'Yes':
        print('\n'+ '\033[1m' + '[WAR]:\t' + message + '\033[0m')
    else:
        print('\033[1m' + '[WAR]:\t' + message + '\033[0m')

def Info(message, toline):
    """
    This function display an information message.

    Paramters:
    ---------
    message:    str,Message to be displayed
    toline:     str,Carriage return or not before the message(Yes or No)

    Returns:
    -------

    """
    if toline == 'Yes':
        print('\n'+ '\033[1m' + '[INF]:\t' + message + '\033[0m')
    else:
        print('\033[1m' + '[INF]:\t' + message + '\033[0m')

def initialize_term():
    '''
    This class clears up the terminal
    '''

    ####### CLEAR the terminal window
    os.system('cls' if os.name == 'nt' else 'clear')
    ##and print the SPARTAN LOGO
    log = TUI_messages().Logo()
    i = 0
    while i < 5:
        if i == 0:
            print('\t '+log[i])
        else:
            print('\t'+log[i])
        i += 1
    print('')
