'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
#####   This file contains
##### the code that removes
##### edges and bad regions
#####  from the spectra
###########################
@License: GPL licence - see LICENCE.txt
'''

##Third party######
import numpy
####################


def main(galaxy, CONF):
    '''
    This function sends the spectrum to be cleaned from edges
    and bad regions, based on the configuration

    Parameters:
    -----------
    galaxy          obj, containing the obj
    CONF            obj, configuration from the user
    '''

        
    if CONF.SPEC['Skip'].lower() == 'yes':
        edges(galaxy, CONF.SPEC['SSkip'], float(CONF.CONF['NSpec']))

    if CONF.SPEC['UseBR'].lower() == 'yes':
        bad_regions(galaxy, CONF.SPEC['BR'])


    
def edges(galaxy, edges, NSpec):
    '''
    '''
    if NSpec == 1:
        wave = galaxy.SPECS[1][3] 
        flux = galaxy.SPECS[1][4]
        err = galaxy.SPECS[1][5]
        edges = float(edges)

        ###select right indexes
        idx = numpy.where(numpy.logical_and(numpy.greater_equal(wave, wave[0]+edges), \
                numpy.less_equal(wave, wave[-1]-edges)))

        new_wave = wave[idx]
        new_flux = flux[idx]
        new_err = err[idx]

        galaxy.SPECS[1][3] = new_wave 
        galaxy.SPECS[1][4] = new_flux
        galaxy.SPECS[1][5] = new_err


    else:
        pass


def bad_regions(galaxy, BR):
    '''
    Remove the bad regions

    Parameters:
    -----------
    galaxy      obj, object we are currently fitting
    BR          str, list of Bad region from the configuration
    '''
    ###get all Bad regions
    BR_first = BR.split(';') 
    BR_final = []
    for i in BR_first:
        BR_final.append(list(map(float, i.split('-'))))


    ###remove them from the spectra
    for i in galaxy.SPECS.keys():
        for j in BR_final:
            wave = galaxy.SPECS[i][3]
            flux = galaxy.SPECS[i][4]
            err  = galaxy.SPECS[i][5]
            ###update the BR applying the redshift
            j[0] = j[0] * (1+galaxy.Redshift)
            j[1] = j[1] * (1+galaxy.Redshift)
            ####if the regions is not in the spectrum we go to 
            ####the next region
            if j[1] < wave[0] or j[0] > wave[-1]:
                continue
            else:
                ###if we have part of the region is in the spectrum
                idx = []
                for k in range(len(wave)):
                    if wave[k] < j[0] or wave[k] > j[1]:
                        idx.append(k)

                galaxy.SPECS[1][3] = wave[idx] 
                galaxy.SPECS[1][4] = flux[idx]
                galaxy.SPECS[1][5] = err[idx]
