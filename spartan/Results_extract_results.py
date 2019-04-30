'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016-18
#####
#####   This file contains
#####   the code that extract
#####   the result in the 
#####       results file
#####
###########################
@License: GPL licence - see LICENCE.txt
'''

####Python General Libraries
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

###third party
import h5py
import numpy


def ListID_dico(fileres):
    '''
    This function extracts the list of object from the result file

    Parameter:
    ----------
    fileres
            str, path to the result file

    Return
    ------
    dicoID
            dict, of couple ID - fitted status
    '''

    dicoID = {}
    with h5py.File(fileres) as ff:
        l = list(ff.keys())
        for i in l:
            dicoID[i] = str(numpy.array(ff['%s/General/Fitted'%i]))[2:-1]
    return dicoID


def ListParameters(fileres, magabsuse):
    '''
    Function that extract the parameter names from the results
    file. For each parameter a distribution will be displayed
    below the general properties table

    Parameter:
    ----------
    fileres     str, file given by the user
    magabsuse   str, yes or no to extract magabs as well

    Returns:
    -------
    List        list of string, with parameter names
    '''

    param = []
    fullList = ['Redshift', 'Npoints', 'Bestchi2']
    with h5py.File(fileres) as ff:
        for i in ff:
            ###extract all the groups
            groups = list(ff[i].keys())
            fitted = str(numpy.array(ff['%s/General/Fitted'%i]))[2:-1]
            ##we extract parameters name only for galaxies that are fitted
            if fitted == 'Fitted':
                if 'Parameters_PDF' in groups:
                    paramindiv = list(ff['%s/Parameters_PDF'%i].keys())
                    for k in paramindiv:
                        p = k+'_PDF'
                        param.append(p)

                if 'Parameters_BF' in groups:
                    paramindiv = list(ff['%s/Parameters_BF'%i].keys())
                    for k in paramindiv:
                        p = k+'_BF'
                        param.append(p)

                if 'Mag_abs' in groups and magabsuse == 'yes':
                    magabs = list(ff['%s/Mag_abs'%i].keys())
                    for k in magabs:
                        p = k+'_ABS'
                        param.append(p)

    List = []
    List += fullList
    List += list(numpy.unique(param))
    return List



def distribution(name, dire, filename):
    '''
    Function that extract all the value in the redsult
    for a given parameter
    Parameter:
    ----------
    name    str, name of the parameter
    dire    str, subdirectory in the hdf5 file where the
                 parameter is stored
    filename str, name of the result file

    Return:
    -------
    values  list, of value for the parameters
    '''
    values = []
    with h5py.File(filename) as ff:
        for i in ff:
            ##we extract values only for fitted galaxies
            fitted = str(numpy.array(ff['%s/General/Fitted'%i]))[2:-1].lower()
            if fitted == 'fitted':
                List =  list(ff['%s/%s'%(i,dire)].keys())
                List += ['Redshift', 'Bestchi2']
                if name in List:
                    extraction = numpy.array(ff['%s/%s/%s'%(i, dire, name)])
                    size = extraction.size
                    ###if single number we check that the value if physical
                    ###avoid -99.9
                    if size == 1 and extraction > -50:
                        values.append(extraction)
                    else:
                        ###we avoid -99.9 values
                        if extraction[0] > -50:
                            values.append(extraction[0])
                if name == 'Npoints':
                    Npoints = [j for j in list(ff['%s/Observable'%i]) if 'Npoints' in j]
                    val = 0
                    for j in Npoints:
                        val += numpy.float(numpy.array(ff['%s/Observable/%s'%(i,j)]))
                    values.append(val)



    return values

def extract_PDF_CDF(filename, ident, P):
    '''
    Method that extract, for a given parameter P
    the PDF and the CDF
    '''
    grid = [0]
    try:
        with h5py.File(filename) as ff:
            ffi = ff['%s/PDF_CDF'%ident]
            for i in ffi:
                if i == P:
                    PDF, CDF, grid = numpy.array(ffi[i])
        if len(grid) <= 1:
            grid = numpy.arange(0,1,0.1)
            PDF = numpy.ones((len(grid)))
            CDF = numpy.ones((len(grid)))

    except:
        grid = numpy.arange(0,1,0.1)
        PDF = numpy.arange(0,1,0.1)
        CDF = numpy.arange(0,1,0.1)
    return grid, PDF, CDF

def extract_full_obj(filename, ident, param, dire, typ):
    '''
    Method that extracts the parameters in the param list
    for a given object
    '''
    allp = []
    with h5py.File(filename) as ff:
        ffi = ff[ident]
        status = str(numpy.array(ffi['General/Fitted']))[2:-1]
        if status == 'Fitted':
            for i in param:
                if i  in ['Redshift', 'Npoints']:
                    p = extract_param_indiv(ffi, i, 'Observable')
                    allp.append(p)
                elif i in ['Bestchi2']:
                    p = extract_param_indiv(ffi, i, 'Template')
                    allp.append(p)
                else:
                    p = extract_param_indiv(ffi, i, dire)
                    allp.append(p)
        return status ,tuple(allp)

def extract_param_indiv(ffi, X, dire):

    ###extract list of parameters
    List =  list(ffi[dire].keys())

    ###if the parameter we want is in the list
    ###we extract the information
    if X in List:
        ##we extract
        extraction = numpy.array(ffi['%s/%s'%(dire, X)])
        ###if we have only one paramter we extract it
        if extraction.size == 1:
            return float(extraction)

        ##if we have more than one number we extract the first
        else:
            return float(extraction[0])

    ###if not we return default value
    else:
        return -99.9

def extract_couple(filename, X, Y):
    '''
    Method that extract all the parameter for a given Id
    Parameter:
    ----------
    ident       str, ident of the object 
    X           str, name of the parameter for X
    Y    str, name of the parameter for Y 

    Return:
    -------
    Xlist  list, of value for the parameter X
    Ylist  list, of value for the parameter Y
    '''

    Xlist = []
    Ylist = []
    with h5py.File(filename) as ff:
        for i in ff:
            ffi = ff[i]
            fitted = str(numpy.array(ffi['General/Fitted']))[2:-1].lower()
            if fitted == 'fitted':
                ###extract 
                typ = X.split('_')
                if X in ['Redshift', 'Npoints']:
                    px = extract_param_indiv(ffi, X, 'Observable')
                elif X in ['Bestchi2']:
                    px = extract_param_indiv(ffi, X, 'Template')
                elif typ[-1] == 'PDF':
                    px = extract_param_indiv(ffi, typ[0], 'Parameters_PDF')
                elif typ[-1] == 'BF':
                    px = extract_param_indiv(ffi, typ[0], 'Parameters_BF')
                elif typ[-1] == 'ABS':
                    px = extract_param_indiv(ffi, typ[0], 'Mag_abs')


                ###extract Y
                typ = Y.split('_')
                if Y in ['Redshift', 'Npoints']:
                    py = extract_param_indiv(ffi, Y, 'Observable')
                elif Y in ['Bestchi2']:
                    py = extract_param_indiv(ffi, Y, 'Template')
                elif typ[-1] == 'PDF':
                    py = extract_param_indiv(ffi, typ[0], 'Parameters_PDF')
                elif typ[-1] == 'BF':
                    py = extract_param_indiv(ffi, typ[0], 'Parameters_BF')
                elif typ[-1] == 'ABS':
                    py = extract_param_indiv(ffi, typ[0], 'Mag_abs')



                Ylist.append(py)
                Xlist.append(px)

    return Xlist, Ylist


def extract_fit(CONF, ident, resfile):
    '''
    Function that extract that select the type of fit that was used by
    the user
    Parameters:
    ----------
    CONF        obj, configuration of the user
    resfile     str, path/and/name of the result file
    ident       str, ID of the galaxy to extract

    Return:
    -------

    '''
    ###select the right type of fit
    if CONF.CONF['UsePhot'].lower() == 'yes' and CONF.CONF['UseSpec'].lower() == 'no':
        toplot = extract_phot(resfile, ident)

    if CONF.CONF['UsePhot'].lower() == 'no' and CONF.CONF['UseSpec'].lower() == 'yes':
        toplot = extract_spec(resfile, ident, int(CONF.CONF['NSpec']))

    if CONF.CONF['UsePhot'].lower() == 'yes' and CONF.CONF['UseSpec'].lower() == 'yes':
        toplot = extract_comb(resfile, ident, int(CONF.CONF['NSpec']))

    return toplot

def extract_spec(filename, ident, Nspec):
    '''
    Function that extracts the spectro fit oif the given ID

    Parameters
    ----------
    filename    str, path/and/name.hdf5 of the result file
    ident       str, ID of the galaxy to extract

    Return
    ------
    fit         list, of fitting data (BFtemp_wave, BFtemp, BF_regrid, SPECS)
    '''

    with h5py.File(filename) as ff:
        obj = ff[ident]

        status = str(numpy.array(obj['General/Fitted']))[2:-1]
        if status == 'Fitted':
            ##extract the observable
            Obs = obj['Observable'] 
            SPECS = {}
            for i in range(Nspec):
                sp = []
                for j in list(Obs.keys()):
                    if j[0:4] == 'spec' and j[-2:] == '_%s'%str(i+1):
                        out = numpy.array(Obs[j])
                        sp.append(out)

                SPECS['%s'%str(i+1)] = sp[::-1]
            
            ## extract the templates
            Temp = obj['Template']
            BFtemp = numpy.array(Temp['Best_template_full'])
            BFtemp_wave = numpy.array(Temp['Best_template_wave'])
            BF_regrid = numpy.array(Temp['Bestfit_newgrid'])

        else:

            BFtemp_wave = [1,2]
            BFtemp = [1,2]
            BF_regrid = [1,2]
            SPECS = {}
            

    fit = [status, BFtemp_wave, BFtemp, BF_regrid, SPECS]    
    return fit




def extract_phot(filename, ident):
    '''
    Function that extracts the photometric fit oif the given ID

    Parameters
    ----------
    filename    str, path/and/name.hdf5 of the result file
    ident       str, ID of the galaxy to extract

    Return
    ------
    fit         list, of fitting data (wavelength, flux, fluxerr, obsmag, 
                       BFtemp, BFtemp_wave, Bestfit_flux, Bestfit_mag)
    '''

    with h5py.File(filename) as ff:
        obj = ff[ident]
 
        ##extract the observable
        Obs = obj['Observable']
        
        status = str(numpy.array(obj['General/Fitted']))[2:-1]
        if status == 'Fitted':
 
            wavelength =  numpy.array(Obs['waveband'])
            flux = numpy.array(Obs['obsflux'])
            fluxerr = numpy.array(Obs['obsfluxerr'])
            obsmag = numpy.array(Obs['obsmag'])

            ## extract the templates
            Temp = obj['Template']
            BFtemp = numpy.array(Temp['Best_template_full'])
            BFtemp_wave = numpy.array(Temp['Best_template_wave'])
            Bestfit_flux = numpy.array(Temp['Bestfit_flux'])
            Bestfit_mag = numpy.array(Temp['Bestfit_mag'])

        else:
            wavelength = []
            flux = []
            fluxerr = []
            obsmag = []
            BFtemp = []
            BTtemp_wave = []
            Bestfit_flux = []
            Bestfit_mag = []
 

    fit = [status, wavelength, flux, fluxerr, obsmag, BFtemp, BFtemp_wave, Bestfit_flux, Bestfit_mag]    
    return fit

def extract_comb(filename, ident, Nspec):
    '''
    Function that extracts the photometric fit oif the given ID

    Parameters
    ----------
    filename    str, path/and/name.hdf5 of the result file
    ident       str, ID of the galaxy to extract
    NSPecs      int, number of spec 

    Return
    ------
    fit         list, of fitting data (wavelength, flux, fluxerr, obsmag, 
                       BFtemp, BFtemp_wave, Bestfit_flux, Bestfit_mag)
    '''
    toplot_phot = extract_phot(filename, ident)
    toplot_spec = extract_spec(filename, ident, Nspec)
 
    with h5py.File(filename) as ff:
        obj = ff[ident]
 
        ##extract the observable
        Obs = obj['Observable']
        
        status = str(numpy.array(obj['General/Fitted']))[2:-1]
        if status == 'Fitted':
            kept_phot = numpy.array(Obs['Kept_phot'])

    return toplot_spec+toplot_phot+[kept_phot]

 
