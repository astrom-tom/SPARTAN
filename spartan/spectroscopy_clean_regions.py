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
    This function cleans the spectrum from the edges.
    Parameters
    ----------
    galaxy  obj, galaxy object with spectrum
    edges   string, size to skip in Angstrom
    Nspec   int, number of spectrum
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
        for i in galaxy.SPECS.keys():
            edge = float(edges.split(';')[i-1])
            
            wave = galaxy.SPECS[i][3] 
            flux = galaxy.SPECS[i][4]
            err = galaxy.SPECS[i][5]

            ###select right indexes
            idx = numpy.where(numpy.logical_and(numpy.greater_equal(wave, wave[0]+edge), \
                numpy.less_equal(wave, wave[-1]-edge)))

            new_wave = wave[idx]
            new_flux = flux[idx]
            new_err = err[idx]

            ##and replace in the spectrum
            galaxy.SPECS[i][3] = new_wave 
            galaxy.SPECS[i][4] = new_flux
            galaxy.SPECS[i][5] = new_err
     
            


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
            brmin = j[0] * (1+galaxy.Redshift)
            brmax = j[1] * (1+galaxy.Redshift)
            ####if the regions is not in the spectrum we go to 
            ####the next region
            if brmax < wave[0] or brmin > wave[-1]:
                continue
            else:
                ###if we have part of the region is in the spectrum
                print(i,j, brmin, brmax)
                idx = []
                for k in range(len(wave)):
                    if wave[k] < brmin or wave[k] > brmax:
                        idx.append(k)

                galaxy.SPECS[i][3] = wave[idx] 
                galaxy.SPECS[i][4] = flux[idx]
                galaxy.SPECS[i][5] = err[idx]
