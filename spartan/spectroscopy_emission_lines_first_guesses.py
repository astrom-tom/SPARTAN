'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016-18
#####
#####   This file contains
##### the code that look at the spectrum
##### and compute the emission lines of some
#####   intense ones (already defined)
###########################
@License: GPL licence - see LICENCE.txt
'''

####third party
import numpy
###############


dico_line = {'H_Lya': [1120, 1195, 1235, 1350, 0],\
             '[OII]': [3690, 3710, 3735, 3755, 10],
             '[OIIIa]': [4929, 4949, 4969, 4989, 0],
             '[OIIIb]': [4969, 4989, 5020, 5040, 0],
             'H_beta': [4830, 4850, 4870, 4890, 0],
             'H_alpha': [6500, 6530, 6580, 6610]}


def check(galaxy, toskip):
    '''
    this method check if some emission line MIGHT
    be present in the spectrum

    Parameter
    ---------
    galaxy      obj, galaxy we fit

    return 
    ------
    dico_line_final     dict, with keyword = name of the line (see input emline file for names)
                              only if 
    '''
    dico_line_final = []
    for i in galaxy.SPECS:
        wave = galaxy.SPECS[i][3]
        spec = galaxy.SPECS[i][4]
        for j in dico_line:
            ###redshift the line
            waveallline = numpy.array(dico_line[j])*(1+galaxy.Redshift)

            ##split by blue and red band pass
            region = []
            k = 0
            while k < len(waveallline)-1:
                region.append([waveallline[k], waveallline[k+1]])
                k+=2

            ###check if the line is in the spectrum
            check = check_validity_of_line(region, wave)

            ##then we compute the mean flux in each region
            if check == 'ok':
                means = []
                meanls = []
                for k in region:
                    meanf, meanl = compute_line_median(k, wave, spec)
                    means.append(meanf)
                    meanls.append(meanl)

                ##finally we compute the EW on the data directly
                EW, line, grid = EWondata(means, meanls, wave, spec, region)

                if EW > dico_line[j][-1]:
                    dico_line_final.append(j)

    return dico_line_final

def EWondata(means, meanls, wave, spec, regions):
    '''
    Function that computes the EW on the spectrum directly
    Parameter:
    ----------
    means       list, of flux en ean bandpass
    meanls      list, of mean wavelength in each band pass
    wave        list, wavelength
    spec        list, fluxes
    regions     list, the two bandpasses
    '''

    ##1-we create a wave grid with 1Ang between the two means
    grid = numpy.arange(meanls[0], meanls[1], 1)

    ##2-we interpolate the continuum in this grid
    cont = numpy.interp(grid, meanls, means)

    ##3 -same for the line
    gridline = numpy.arange(regions[0][1], regions[1][0], 1)

    ##4-we retrieve the spectrum in this region
    line = numpy.interp(gridline, wave, spec)

    ##5 we interpolate the cont in the region line
    contl = numpy.interp(gridline, grid, cont)

    ##4 and compute the EW 
    EW = numpy.trapz(1-(line/contl))

    return EW, line, gridline


def compute_line_median(region, wave, spec):
    '''
    Method that compute the median flux in the region bandpass
    Parameter
    --------
    region      list, of 2 wavelength defining the bandpass
    wave        list, of observed wavelength
    spec        list, of observed flux

    return
    ------
    mean      float, value of the mean flux
    meanl     float, wavelength of the mean flux
    '''
    
    meanl = region[0] + (region[1]-region[0])/2
   
    meanlist = []
    for i in range(len(wave)):
        if region[0] < wave[i] < region[1]:
            meanlist.append(spec[i])
    if len(meanlist) == 0:
        return numpy.nan, meanl

    else: 
        return numpy.nanmean(meanlist), meanl



def check_validity_of_line(region, wave):
    '''
    Method that checks if the line is in the spectrum
    in term of lambda
    Parameters
    ----------
    region      list, of 2 list (each with li lf) of the band pass of the line
    wave        list, of wavelength of the spectrum

    return
    ------
    check       str, 'ok' or 'no'
    '''
    ###we give a tolerance
    dl1 = (region[0][1] - region[0][0])/2
    dl2 = (region[1][1] - region[1][0])/2

    if region[0][0] - dl1/2 > wave[0] and region[1][1]+dl2/2 < wave[-1]:
        check = 'ok'
    else:
        check = 'no'

    return check

