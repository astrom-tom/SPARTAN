'''
The SPARTAN Project
-------------------
This module save results in the disk

@author: R. THOMAS
@year: 2016
@place: UV/LAM/UCBJ
@License: GPL v3.0 - see LICENCE.txt
'''
##Python LIB
import os
import sys
##############

###Third party
import numpy
import h5py
###############

def save_to_file_fail(resfile, galaxy, CONF):
    '''
    This method saves the status of the fit if Fitted = 'No' in the main of the
    fit
    Parameter
    ---------
    ID          str, ID of the object
    resfile     str, path/and/name of the result file
    CONF        obj, configuration from the user

    Return
    ------
    NONE
    '''
    with h5py.File(resfile) as Res:
        ## we look for the fitting status
        Fitted = str(numpy.array(Res['%s/General/Fitted'%galaxy.ID]))[2:-1]
        ## We update ToFit accordingly to the status reported
        ## in the result file
        if Fitted == 'Fitted' and CONF.FIT['OverFit'].lower()  == 'yes':
            ##if we already fitted t
            del Res['%s'%galaxy.ID]
         
    ##open the result file and save the status as 'FAIL'
    with h5py.File(resfile) as Res:
        try:
            del Res['%s'%galaxy.ID]
        except:
            pass
        obj = Res.create_group(galaxy.ID)
        gen = Res.create_group('%s/General'%galaxy.ID)
        gen.create_dataset('Fitted', data=numpy.string_('FAIL'))

def save_phot(Results, galaxy, CONF):
    '''
    This function saves the results of the studied objet
    into the result file
    Parameter
    ---------
    Results     dict, of the results
    galaxy      objct, galaxy object with results
    CONF        dict, configuration of the user

    Return
    ------
    '''

    ###first we have to check if some data where already in the result file
    deleted = 0
    with h5py.File(Results, 'a') as Res:
        ## we look for the fitting status
        Fitted = str(numpy.array(Res['%s/General/Fitted'%galaxy.ID]))[2:-1]
        ## We update the result file accordingly to the status reported
        ## in the result file and the overfit choice.
        if galaxy.status == 'Fitted' and CONF.FIT['OverFit'].lower() == 'yes':
            del Res['%s'%galaxy.ID]
            deleted = 1

    ##open the result file and save the results
    with h5py.File(Results) as Res:
       
        if deleted == 0:
            del Res['%s'%galaxy.ID]

        #-1-# general information
        obj = Res.create_group(galaxy.ID)
        gen = Res.create_group('%s/General'%galaxy.ID)
        gen.create_dataset('Fitted', data=numpy.string_(galaxy.status))
        #[print(numpy.array(gen[i])) for i in list(gen.keys())]

        #-2-# Observable directory
        Obs = Res.create_group('%s/Observable'%galaxy.ID)
        Obs.create_dataset('Redshift', data = numpy.array(galaxy.Redshift))
        Obs.create_dataset('Npoints', data = numpy.array(galaxy.Nband))
        Obs.create_dataset('waveband', data = numpy.array(galaxy.waveband))
        Obs.create_dataset('obsmag', data = numpy.array(galaxy.obsmag))
        Obs.create_dataset('obserr', data = numpy.array(galaxy.obserr))
        Obs.create_dataset('obsflux', data = numpy.array(galaxy.obsflux))
        Obs.create_dataset('obsfluxerr', data = numpy.array(galaxy.obsfluxerr))
        Obs.create_dataset('Names_mag', data = [numpy.string_(i) for i in galaxy.Names])
        Obs.create_dataset('Upper_limits', data = [numpy.string_(i) for i in galaxy.uppers])
        #[print(numpy.array(Obs[i])) for i in list(Obs.keys())]

        #-2-# Template directory 
        Temp = Res.create_group('%s/Template'%galaxy.ID)
        Temp.create_dataset('Bestchi2', data = galaxy.bestchi2red) 
        Temp.create_dataset('Best_template_full', data = galaxy.besttemplate)
        Temp.create_dataset('Bestfit_mag', data = galaxy.bestfit_mag[0])
        Temp.create_dataset('Bestfit_flux', data = galaxy.bestfit_flux)
        Temp.create_dataset('Best_template_wave', data = galaxy.besttemplate_wave)
        #[print(numpy.array(Temp[i])) for i in list(Temp.keys())]

        #-3-# BF Parameter directory 
        ParametersBF = Res.create_group('%s/Parameters_BF'%galaxy.ID) 
        for i in list(galaxy.BFparam.keys()):
            ParametersBF.create_dataset(i, data = numpy.array(galaxy.BFparam[i]))

        #-4-# PDF Parameter directory 
        ParametersPDF = Res.create_group('%s/Parameters_PDF'%galaxy.ID) 
        PDFCDF = Res.create_group('%s/PDF_CDF'%galaxy.ID) 

        for i in list(galaxy.chi2p.keys()):
            m   = galaxy.chi2p[i][0]
            m1  = galaxy.chi2p[i][2]
            p1  = galaxy.chi2p[i][1]
            #print(m, m1, p1)
            grid = galaxy.chi2p[i][3]
            pdf = galaxy.chi2p[i][4]
            cdf = galaxy.chi2p[i][5]
            ParametersPDF.create_dataset(i, data = numpy.array([m, m1, p1]))
            PDFCDF.create_dataset(i, data = numpy.array([pdf, cdf, grid]))

        #-5-# Absolute Magnitude
        Magabs = Res.create_group('%s/Mag_abs'%galaxy.ID) 
        for i in range(len(galaxy.MagAbs['Name'])):
            M = galaxy.MagAbs['Meas'][i]
            Magabs.create_dataset(galaxy.MagAbs['Name'][i], data = numpy.array(M))
        #[print(numpy.array(Magabs[i])) for i in list(Magabs.keys())]


def save_spec(Results, galaxy, CONF):
    '''
    This function saves the results of the studied objet
    into the result file
    Parameter
    ---------
    Results     dict, of the results
    galaxy      obj, galaxy object with results
    CONF        dict, configuration of the user

    Return
    ------
    '''

    ###first we have to check if some data where already in the result file
    deleted = 0
    with h5py.File(Results, 'a') as Res:
        ## we look for the fitting status
        Fitted = str(numpy.array(Res['%s/General/Fitted'%galaxy.ID]))[2:-1]
        ## We update the result file accordingly to the status reported
        ## in the result file and the overfit choice.
        if galaxy.status == 'Fitted' and CONF.FIT['OverFit'].lower() == 'yes':
            del Res['%s'%galaxy.ID]
            deleted = 1

    ##open the result file and save the results
    with h5py.File(Results) as Res:
       
        if deleted == 0:
            del Res['%s'%galaxy.ID]

        #-1-# general information
        obj = Res.create_group(galaxy.ID)
        gen = Res.create_group('%s/General'%galaxy.ID)
        gen.create_dataset('Fitted', data=numpy.string_(galaxy.status))

        #-2-# Observable directory
        Obs = Res.create_group('%s/Observable'%galaxy.ID)
        Obs.create_dataset('Redshift', data = numpy.array(galaxy.Redshift))
        Obs.create_dataset('Nspec', data = numpy.array(int(CONF.CONF['NSpec'])))

        specs = ['specwave', 'specflux', 'specerr', 'mags', 'mags_flux', 'mags_Leff', 'mags_Tran'] 
        for i in galaxy.SPECS.keys():
            for j in specs:
                if j == 'mags':
                    Obs.create_dataset('%s_%s'%(j,i),\
                            data = [numpy.string_(i) for i \
                            in numpy.array(galaxy.__dict__['%s_%s'%(j,i)])]) 
                else:
                    Obs.create_dataset('%s_%s'%(j,i), \
                            data = numpy.array(galaxy.__dict__['%s_%s'%(j,i)]))

            ###number of point / spec
            Obs.create_dataset('Npoints_%s'%i, \
                    data = numpy.array(len(numpy.array(galaxy.__dict__['specwave_%s'%(i)]))))

        #-3-# BF Parameter directory 
        ParametersBF = Res.create_group('%s/Parameters_BF'%galaxy.ID) 
        for i in list(galaxy.BFparam.keys()):
            ParametersBF.create_dataset(i, data = numpy.array(galaxy.BFparam[i]))


        #-2-# Template directory 
        Temp = Res.create_group('%s/Template'%galaxy.ID)
        Temp.create_dataset('Bestchi2', data = galaxy.bestchi2red) 
        Temp.create_dataset('Best_template_full', data = galaxy.besttemplate)
        Temp.create_dataset('Best_template_wave', data = galaxy.besttemplate_wave)
        Temp.create_dataset('Bestfit_newgrid', data = galaxy.regrid_template)
        Temp.create_dataset('Bestfit_newgrid_wave', data = galaxy.regrid_wave)

        #-4-# PDF Parameter directory 
        ParametersPDF = Res.create_group('%s/Parameters_PDF'%galaxy.ID) 
        PDFCDF = Res.create_group('%s/PDF_CDF'%galaxy.ID) 

        for i in list(galaxy.chi2p.keys()):
            m   = galaxy.chi2p[i][0]
            m1  = galaxy.chi2p[i][2]
            p1  = galaxy.chi2p[i][1]
            #print(m, m1, p1)
            grid = galaxy.chi2p[i][3]
            pdf = galaxy.chi2p[i][4]
            cdf = galaxy.chi2p[i][5]
            ParametersPDF.create_dataset(i, data = numpy.array([m, m1, p1]))
            PDFCDF.create_dataset(i, data = numpy.array([pdf, cdf, grid]))
