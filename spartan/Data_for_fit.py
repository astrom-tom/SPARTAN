'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
#####   This file contains
#####   the code that extract the
#####   sample to fit from the 
#####       *dat.hdf5
#####
###########################
@License: GPL licence - see LICENCE.txt
'''

####Python Standard Libraries
import warnings
import time
warnings.simplefilter(action='ignore', category=FutureWarning)
#############################

########python third party
import h5py
import numpy
###########################

###local libraries#####################
from . import Results_PDF as PDF
from . import photometry_Mag_abs as Mag_abs
from . import messages as MTU
from . import spectroscopy_extract_data_spec as extract
########################################

def sample_to_fit(Datafile, Resfile, Overfit):
    """
    This function retrive the list of all the object that are in the
    datafile and checks them
    Parameter:
    ----------
    Datafile        str, path/and/file.hdf5 to data file (*_dat.hdf5)
    Overfit         str, to allow overfit ot not (from the configuration 
                            of the user)

    Return:
    ------
    OBS             list, of object id
    """
    OBS = ListID(Datafile)
    return check_sample(OBS, Resfile, Overfit)


def ListID(File):
    '''
    This function extract the list of ID of a given SPARTAN file
    Parameter
    ---------
    File        str, path/and/name to file
    '''
    with h5py.File(File) as F:
        OBS = list(F.keys()) 
    return OBS
 
def ListID_dico(File):
    '''
    Function that return the list of ident contained in
    the file
    Parameter:
    ----------
    fileres     str, file given by the user

    Returns:
    -------
    dico     dictionnary, keywords: idents and data: fitted status
    '''
    dico = {}
    with h5py.File(File) as ff:
        for i in ff:
            fitted = str(numpy.array(ff['%s/General/Fitted'%i]))[2:-1].lower()
            dico[i] = fitted
    return dico

def check_sample(IDs, resfile, Overfit):
    '''
    This method checks the whole sample to extract the 
    sample to be fitted

    Parameter:
    ----------
    IDs     list, of ID in the data file
    resfile str, path/and/name of the result file
    Overfit str, if the user allow the overfit or no

    return:
    -------
    Tobefitted  list,   of ID to be fitted
    '''
    Tobefitted = []
    for i in IDs:
        tofit = check_results(i, resfile, Overfit)
        if tofit == 'YES':
            Tobefitted.append(i)

    return Tobefitted

def check_results(ID, resfile, Overfit):
    '''
    This methods check if the fit as already been done AND SAVED
    in the result file. If so, we check if the 
    Parameter
    ---------
    ID          str, ID of the object
    Overfit     str, if the user allow the overfit or no
    resfile     str, path/and/name of the result file
    
    Return
    ------
    ToFIT       str, yes or no to fit the object
    '''
    ToFit = 'NO'
    ##open the library and extract models
    with h5py.File(resfile, 'r') as Res:
        ## we look for the fitting status
        if ID in list(Res.keys()):

            Fitted = str(numpy.array(Res['%s/General/Fitted'%ID]))[2:-1]
            ## We update ToFit accordingly to the status reported
            ## in the result file

            if Fitted == 'Fitted' and Overfit.lower() == 'no':
                ##if we already fitted the object and the user
                ## does not allow overfit we won't refit the object
                MTU.Info('Obj: %s -->Object already fitted'%ID, 'No')
                MTU.Info('You do not allow overfit...Go to next object', 'No')
                ToFit = 'NO'

            elif Fitted == 'Fitted' and Overfit.lower() == 'yes':
                ##if we already fitted the object but the user
                ## allows overfit we will refit the object
                #MTU.Info('Obj: %s --> Object already fitted'%ID, 'No')
                #MTU.Info('You allow overfit...Continue', 'No')
                ToFit = 'YES'

            elif Fitted == 'FAIL':
                MTU.Info('Obj: %s -->failed at first pass, we will not refit'%ID, 'No')
                ToFit = 'No'
            
            elif Fitted == 'NO':
                ToFit = 'YES'
        else:
            ToFit = 'NO'

    return ToFit

class indiv_obj:
    '''
    this class creates an object corresponding to a galaxy
    '''
    def __init__(self, Datafile, ID, fit_type, CONF):
        '''
        This methods defines the attributes

        Parameters:
        -----------
        Datafile    str, path/to/file.hdf5 file with data
        ID          str, ID of the galaxy to be fitted
        fit_type    str, 'mag', 'spec' or 'comb'
        CONF        obj, configuration of the user

        Attributes:
        -----------
        Magnitudes  list, of magnitude of the given object
        Redshift    float, redshift of the galaxy
        '''
        if fit_type == 'mag':
            with h5py.File(Datafile, 'r') as Data:
                self.Magnitudes = numpy.array(Data['%s/Mag'%ID]).astype('str')
                self.Redshift = float(Data['%s/z'%ID][()])
                self.ID = ID

        if fit_type == 'spec':
            with h5py.File(Datafile, 'r') as Data:
                self.ID = ID
                objecT = Data['%s'%ID]
                datasets = list(objecT)
                self.Redshift = float(Data['%s/z'%ID][()])
                self.SPECS, NormT = extract.extract_datasets(datasets, objecT, CONF, self.Redshift)
                for i in NormT:
                    if i[0][0] != 'door':
                        i[0] = str(i[0])[2:-1]
                self.NormT = NormT
                self.Magnitudes_spec = self.NormT

        if fit_type == 'comb':
            with h5py.File(Datafile, 'r') as Data:
                self.Magnitudes = numpy.array(Data['%s/Mag'%ID]).astype('str')
                self.Redshift = float(Data['%s/z'%ID][()])
                self.ID = ID
                objecT = Data['%s'%ID]
                datasets = list(objecT)
                self.SPECS, NormT = extract.extract_datasets(datasets, objecT, CONF, self.Redshift)
                for i in NormT:
                    if i[0][0] != 'door':
                        i[0] = str(i[0])[2:-1]
                self.NormT = NormT
                self.Magnitudes_spec = self.NormT
                self.limits = []
                for i in range(int(CONF.CONF['NSpec'])):
                    w = self.SPECS[i+1][3]
                    self.limits.append((min(w), max(w)))


    def best_chi2(self, chi2, besttemp, bestfitmag, bestfitflux, wave, index, fittype):
        '''
        Methods that creates galaxy object attributes related to the best fit
        template

        Parameters:
        -----------
        chi2        float, bestchi2
        besttemp    np array, best full template
        bestfitmag  nparray, best fit magnitude template
        bestfitflux nparray, best fit mag (in flux)
        wave        nparray, wavelentght og the full tempalte
        index       int, index of the bestchi2 template in the global array

        New attributes:
        ---------------
        bestchi2red         
        besttemplate
        bestfit_mag
        bestfit_flux
        besttemplate_wave
        '''
        if fittype == 'mag':
            self.bestchi2red = chi2
            self.besttemplate =  besttemp
            self.bestfit_mag =  bestfitmag
            self.bestfit_flux = bestfitflux
            self.besttemplate_wave = wave 
            self.bestfit_index = index

        if fittype == 'spec':
            self.bestchi2red = chi2
            self.besttemplate =  besttemp
            self.besttemplate_wave = wave
            self.regrid_template = bestfitmag 
            self.bestfit_index = index

        if fittype == 'comb':
            self.bestchi2red = chi2
            self.besttemplate =  besttemp
            self.regrid_template = bestfitflux 
            self.bestmags = bestfitmag
            self.besttemplate_wave = wave
            self.bestfit_index = index




    def create_observable(self, Photofit, fit_type):
        '''
        Method that create the observable attributes of the galaxy

        Parameter
        ---------
        Photofit    obj, photometry for fit

        New attributes
        --------------
        obsmag      observed mags
        obserr      observed magnitude errors
        obsflux     obsserved flux
        obsfluxerr  observed error in flux unit
        Nband       number of observed band use for the fit
        waveband    wavelength of the bands
        '''
        self.obsmag = Photofit.Meas
        self.obserr = Photofit.err
        self.waveband = Photofit.Leff_all_bands
        self.Nband = len(Photofit.Meas)
        self.obsflux = Photofit.flux_all_bands
        self.obsfluxerr = Photofit.fluxerr_all_bands
        self.Names = Photofit.Names
        self.uppers = Photofit.upper_limits
        if fit_type == 'comb':
            self.kept_mags = Photofit.kept
            


    def create_observable_spec(self,):
        '''
        Method that create the observable attributes of the galaxy

        Parameter
        ---------
        Photofit    obj, photometry for fit

        New attributes
        --------------
        obsmag      observed mags
        obserr      observed magnitude errors
        obsflux     obsserved flux
        obsfluxerr  observed error in flux unit
        Nband       number of observed band use for the fit
        waveband    wavelength of the bands
        '''
        
        for i in self.SPECS.keys():
            mags = self.SPECS[i][:3]
            if mags[0] != 'door':
                mags[0] = str(mags[0])[2:-1]
            specwave = self.SPECS[i][3]  
            specflux = self.SPECS[i][4]
            specerr = self.SPECS[i][5]
            setattr(self, 'mags_%s'%i, mags)
            setattr(self, 'specwave_%s'%i, specwave )
            setattr(self, 'specflux_%s'%i, specflux)
            setattr(self, 'specerr_%s'%i, specerr)



    def Bf_param(self, lib, Norm):
        '''
        Method that create the BFparam attributes of the galaxy
        parameter
        ---------
        lib     obj, library of template
        Norm    float, Normalisation of the best template fit

        New attributes
        --------------
        BFdict      dictionnary of BF parameters
        '''
        ###transform Name of the param + values to
        ###a dictionnary Dict['Name param'] = value
        name = lib.Names
        V = lib.array_param[self.bestfit_index][0]
        Dico = {}
        for i,j in zip(name, V):
            if i == 'M*':
                if j != 0.0:
                    Dico[i] = numpy.log10(j*Norm) 
                else:
                    Dico[i] = -99.9
            elif i == 'SFR':
                if j != 0.0:
                    Dico[i] = numpy.log10(j*Norm)
                else:
                    Dico[i] = -99.9
            else:
                Dico[i] = j

        ##and create the attribute
        self.BFparam = Dico
        

    def chi2param(self, lib, Proba, Norm, CONF):
        '''
        Method that computes the PDF parameters for the galaxy being fitted
        Parameters
        ----------
        lib     obj, library of template
        Proba   array, of prabability
        Norm    array, of normalization
        CONF    dict, of configuration from user

        Attributes
        ----------
        chi2param dict, of chi2 parameters
        '''

        self.chi2p = PDF.main(lib.array_param, lib.Names, Proba, Norm, CONF, \
                self.BFparam, self.Redshift)

    def magabs(self, CONF,COSMOS):
        '''
        Method that computes the mag_abs for the galaxy being fitted

        Parameter
        ---------
        COSMOS_obj  dict, with cosmological properties

        Attributes
        ----------
        MagAbs      dictionnary of magabs     
        '''
        M = Mag_abs.main([self.besttemplate_wave, self.besttemplate], CONF, self.Redshift, COSMOS)  
        self.MagAbs = M
        
        
