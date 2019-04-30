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
from matplotlib import gridspec

def combfit(galaxy, CONF):
    '''
    Module that plot a template with magnitude on top
    '''
    #print(galaxy.__dict__.keys())

    #first subplot
    fig = plt.figure()
    aa = fig.add_subplot(111)

    minx = []
    maxx = []
    miny = []
    maxy = []

    ##spectrum
    for i in range(int(CONF.CONF['NSpec'])):
        wave = galaxy.__dict__['specwave_%s'%str(int(i+1))]
        flux = galaxy.__dict__['specflux_%s'%str(int(i+1))]
        minx.append(min(wave))
        maxx.append(max(wave))
        miny.append(min(flux))
        maxy.append(max(flux))

        aa.plot(wave,flux, color='k', \
                zorder=-1, alpha=0.5, lw=0.5)

    #minx.append(min(galaxy.waveband[galaxy.kept_phot]))
    #maxx.append(max(galaxy.waveband[galaxy.kept_phot]))
    #miny.append(min(galaxy.obsflux[galaxy.kept_phot]))
    #maxy.append(max(galaxy.obsflux[galaxy.kept_phot]))


    aa.scatter(galaxy.waveband[galaxy.kept_phot], galaxy.obsflux[galaxy.kept_phot],\
            color='r', zorder=0)

    aa.plot(galaxy.besttemplate_wave, galaxy.besttemplate, color='b', lw=1)
    aa.set_title('combined')
    
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
