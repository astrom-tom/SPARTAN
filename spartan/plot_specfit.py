'''
###########################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
#####   spec fit plot
#####
###########################
@License: GPL licence - see LICENCE.txt
'''

import matplotlib.pyplot as plt
from matplotlib import gridspec

def specfit(tempwave, template, regrid, SPECS):
    '''
    Module that plot a template with magnitude on top
    '''
    #first subplot
    fig = plt.figure()
    aa = fig.add_subplot(111)
    ##plot the template and magnitudes

    minx = []
    maxx = []
    miny = []
    maxy = []

    for i in SPECS.keys():
        minx.append(min(SPECS[i][3]))
        maxx.append(max(SPECS[i][3]))
        miny.append(min(SPECS[i][4]))
        maxy.append(max(SPECS[i][4]))

        aa.plot(SPECS[i][3], SPECS[i][4], color='k', lw=0.5, alpha=0.5)

    #aa.plot(SPECS[1][3], regrid[0], color='r')
    aa.plot(tempwave, template, label='Template-chi2', color='b', lw=1.)
    print(len(tempwave))
    aa.set_title('spec')
    
    ##formatting
    aa.set_ylabel('Flux density (erg/s/cm2/AA)', fontsize =8)
    aa.minorticks_on()
    aa.set_xlim([min(minx)-1500, max(maxx)+1500])
    aa.set_ylim([min(miny), max(maxy)])
    #aa.xaxis.set_major_formatter(plt.NullFormatter())
    aa.legend(fontsize=15)
    #aa.set_yscale('log')
    #aa.set_xscale('log')

    plt.show() 
