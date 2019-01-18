'''
###########################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
#####   photo fit plot
#####
###########################
@License: GPL licence - see LICENCE.txt
'''

import matplotlib.pyplot as plt

def cleaning_plot(galaxy_before, galaxy_after):
    '''
    Module that plot a template with magnitude on top
    '''

    fig = plt.figure()
    aa = fig.add_subplot(111)

    flux_bef = galaxy_before.SPECS[1][4]
    wave_bef = galaxy_before.SPECS[1][3]
    err_bef = galaxy_before.SPECS[1][5]


    flux_aft = galaxy_after.SPECS[1][4]
    wave_aft = galaxy_after.SPECS[1][3]
    err_aft = galaxy_after.SPECS[1][5]

    aa.plot(wave_bef/(1+galaxy_after.Redshift), flux_bef, lw=2, color='r')
    aa.plot(wave_aft/(1+galaxy_after.Redshift), flux_aft, lw=1, color='k', ls='--')


    aa.minorticks_on()
    aa.set_xlabel('Wavelength')
    aa.set_ylabel('Flux density')
    plt.show() 
