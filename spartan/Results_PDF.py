'''
The SPARTAN Project
-------------------
This module save results in the disk

@author: R. THOMAS
@year: 2016
@place: UV/LAM/UCBJ
@License: GPL v3.0 - see LICENCE.txt
'''
##Python Standard
import os
import time
####################

####Third party#######################################
import numpy
import scipy
import h5py
from scipy.ndimage.filters import gaussian_filter
from matplotlib import pyplot as plt
####################################################
    
def main(Parameter, Name, Proba, Norm, CONF, paramBF, Redshift):
    '''
    Main function of PDF-x2 computing.

    Parameter
    ---------
    parameter   Ndarray, parameter values of the library
    Name        List, of string --> parameter names
    results     Results, dict of results
    CONF        configuration, of Spartan

    Return
    ------
    results,    dict, with parameter estimation values

    '''
    ## 1- we prepare the parameter array with scales
    ## every parameter that have to be computed in log must 
    ## be transformed
    result = {}
    for i in range(len(Name)):
        if Name[i] in ['M*', 'SFR']:
            a = Parameter.T[i]*Norm
            nonzero = numpy.where(a!=0)
            A = numpy.log10(a[nonzero])
            ## 2- we compute the PDF with CHI2 proba
            Xc, plusc, minusc, gridc, PDFc, CDFc = continuous_param(A, Proba, Name[i])
            ## 3- and save them in results
            result[Name[i]] = (Xc, +plusc, minusc, gridc, PDFc, CDFc)
        

        ####if mean IGM the transmission are fixed no error computation
        elif Name[i][0:2]=='Tr':
            ###if the IGM is mean, or the redshift <1.5, we have only one value-->no PDF
            ##computed, we take the best fit value
            if CONF.LIB['IGMtype']=='mean_meiksin' or CONF.LIB['IGMtype']=='mean_madau' or\
                   Redshift < 1.5 :
                result[Name[i]] = (paramBF[Name[i]], -99.9, -99.9, [], [], [])
                
            else:
                ####if the IGM is free, we compute the PDF with the discrete function
                A = Parameter.T[i]
                Xd, plusd, minusd, gridd, PDFd, CDFd = discrete_param(A,Proba)
                result[Name[i]] = (Xd, plusd, minusd, gridd, PDFd, CDFd)
        
        elif Name[i] == 'Dust_curve':
            result[Name[i]] = (paramBF[Name[i]], -99.9, -99.9, [], [], [])

        ###else, we do the same for descrete parameters
        else:
            A = Parameter.T[i]
            Xd, plusd, minusd, gridd, PDFd, CDFd = discrete_param(A,Proba)
            result[Name[i]] = (Xd, plusd, minusd, gridd, PDFd, CDFd)
        
    return result


def discrete_param(param_list, proba):
    '''
    Method that compute the PDF of a parameter that has a discrte 
    distribution
    '''
    rawgrid = numpy.unique(param_list)
    ##we copute the bin
    ##to do so we create an array where all the elements are shifted by one position
    ##and compute the difference between the original array
    raw_roll = numpy.roll(rawgrid,1)
    dif = rawgrid-raw_roll
    meanbin = numpy.mean(dif[numpy.where(dif>0)[0]])

    ##we add an extra bin at the end and at the beginning
    if min(rawgrid)-meanbin < 0:
        Xgrid = [0]
    else: 
        Xgrid = [min(rawgrid)-meanbin]
    for i in rawgrid:
        Xgrid.append(i)
    Xgrid.append(max(rawgrid)+meanbin)

    ##create the 1d array for Proba values
    values_PDF = numpy.zeros((len(Xgrid)))
    for i in enumerate(Xgrid):
        index = numpy.where(param_list==Xgrid[i[0]])
        values_PDF[i[0]] = numpy.sum(proba[index]) 
  
    ####if very bad fit --> no PDF can be computed
    if sum(values_PDF) == 0.0:
        return -99.9, -99.9, -99.9, [], [], []

    ##then normalize the PDF 
    values_PDF = values_PDF / sum(values_PDF)
    ##Make the CDF
    CDF = numpy.cumsum(values_PDF)

    ##if we just have a peak
    if len(numpy.where(values_PDF==1.0)[0]) == 1:
            idxpeak = numpy.where(values_PDF==1.0)[0][0]
            X = Xgrid[idxpeak]
            minus = Xgrid[idxpeak-1]
            plus = Xgrid[idxpeak+1]

    else:
        #And compute values
        idx = (numpy.abs(CDF-0.5)).argmin()
        X = Xgrid[idx]

        idxl = (numpy.abs(CDF-0.05)).argmin()
        minus = Xgrid[idxl]

        idxh = (numpy.abs(CDF-0.95)).argmin()
        plus = Xgrid[idxh]
     
    ##For plot CDF and PDF
    #plot().plot_PDF_CDF(Xgrid, values_PDF, Xgrid, CDF )        
    '''
    fig = plt.figure()
    aa = fig.add_subplot(121)
    aa.plot(Xgrid, values_PDF)
    ab = fig.add_subplot(122)
    ab.plot(Xgrid, CDF)
    plt.show()
    '''
    
    return float(X), float(plus), float(minus), Xgrid, values_PDF, CDF


def continuous_param(param_list, proba, name):
    '''
    Method that extract X+/-sigma for a continuous parameter
    like Mass or SFR
    '''
    ###just in case there are some -inf values
    Good_index = numpy.where(param_list > -100)
    param_list = param_list[Good_index]
    proba = proba[Good_index]

    ##define the edges of the PDF
    #if name == 'SFR':
    minimum = min(param_list)
    maximum = max(param_list)
        #minimum = -7.0
        #maximum = 7.0

    #if name == 'M*':
    #    minimum  = 4.0
    #    maximum  = 16.0
    ##and the number of bins of the PDF
    Nbin = 250
    ##then we create the grid of the parameter
    ##first the step
    s = (maximum-minimum) / Nbin
    grid = numpy.arange(minimum, maximum, s)
    values_PDF = numpy.zeros(grid.shape)

    ##and populate the grid
    i=0
    while i < len(grid):
        index_bin = numpy.where( numpy.logical_and( param_list > grid[i]-s/2 \
                , param_list <= grid[i]+s/2) )
        values_PDF[i] = numpy.sum(proba[index_bin])    
        i += 1

    ####if very bad fit --> no PDF can be computed
    if sum(values_PDF) == 0.0:
        return -99.9, -99.9, -99.9, [], [], []

    ##then normalize the PDF 
    values_PDF = values_PDF / numpy.sum(values_PDF)

    ##Make the CDF
    CDF = numpy.cumsum(values_PDF)
    #CDFinterp = numpy.arange(0, 1, 0.01)
    #grid_CDF = numpy.interp(CDFinterp, CDF, grid)
    
    ##For plot CDF and PDF
    #plot().plot_PDF_CDF(grid, values_PDF, grid, CDF )        
    
    #And compute values
    #X = grid_CDF[numpy.where(CDFinterp == 0.5)]
    #plus = grid_CDF[numpy.where(CDFinterp == 1-0.08)] - X
    #minus = X -grid_CDF[numpy.where(CDFinterp == 0.08)]
  
    if len(numpy.where(values_PDF==1.0)[0]) == 1:     
        idxpeak = numpy.where(values_PDF==1.0)[0][0]
        X = grid[idxpeak]
        if idxpeak + 1 == len(grid):
            minus = grid[idxpeak-1]
            plus = grid[idxpeak]
        elif idxpeak == 0:
            minus = grid[idxpeak]
            plus = grid[idxpeak+1]
        else:
            minus = grid[idxpeak-1]
            plus = grid[idxpeak+1]


    else:
        idx = (numpy.abs(CDF-0.5)).argmin()
        X = grid[idx]

        idxl = (numpy.abs(CDF-0.05)).argmin()
        minus = grid[idxl]


        idxh = (numpy.abs(CDF-0.95)).argmin()
        plus = grid[idxh]
        
    return float(X), float(plus), float(minus), grid, values_PDF, CDF


