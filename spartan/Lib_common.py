'''
The SPARTAN project
-------------------
This module gathers deals with the library. It extract it,
select templates of the right age, and put it at z

@author: R. THOMAS
@year: 2016-17
@place: UV/LAM/UCBJ/ESO
@License: GPL licence - see LICENCE.txt
'''
##Python LIB
import os
import warnings
import time
warnings.simplefilter(action='ignore', category=FutureWarning)
##############################

###third party################
import numpy
import scipy
from scipy.ndimage.filters import gaussian_filter
import h5py
###########################

###Local imports##########
from .units import Phys_const
from .      import messages as MTU
######################

#----------------------------------------------------------------------

class LIB:
    def __init__(self, LIBfile):
        '''
        Module that load the Library of template selected by the user
        Parameter:
        ----------
        LIBfile     str, /path/and/file_LIB.hdf5    to the library
        
        Attribute:
        ---------
        Wave_final          numpy array, common wavelength of all the template  
        Templates_final         ''     , flux of the template
        Parameter_array         ''     , Parameter of the template
        Names               ''     , Name of the parameter
        Cosmo_templates         '' , Template with an age lower than the age of the 
                                      universe at a given redshift
        Cosmo_param             '' , Parameter of the Cosmo_templates
        Wave_at_z               '', template wavelength at the considered redshift
        Temp_at_z               '', Flux of the tempalte at the considered redshift
        '''
        ##open the library and extract models
        with h5py.File(LIBfile) as LIB:
            wave = numpy.array(LIB['Wavelength'])
            Templates = numpy.array(LIB['Templates'])
            Names_parameters = numpy.array(LIB['Parameter']).tolist()
        
        Names_str = []
        for i in Names_parameters:
            if str(i)[0] == 'b':
                Names_str.append(str(i)[2:-1])
            else:
                Name_str.append(i)


        ##as parameters are given inside the templates 
        ##themselves (see LIB construction)
        ## we must find where they are. In the wavelength list they are
        ## marked as -99.9. So:
        Physical_index = numpy.max(numpy.where(wave == -99.9))
        self.Wave_final = wave[Physical_index+1:]
        self.Templates_final = Templates[:, Physical_index+1:]
        self.Parameter_array = Templates[:, :Physical_index+1]
        self.Names = Names_str

    def Make_cosmological_Lib(self, Cosmo_obj, T_emline, COSMO_conf):
        '''
        This method makes the cosmological library, i-e, it removes the ages above
        of the age of the universe from the given library.

        Parameter
        ---------
        Cosmo_obj   dict, cosmological information at the redshift of the object
                          we are studying
        T_emline    numpy array, Template with emission lines
        COSMO_conf  dict   , of cosmological configuration by the user

        Attributes
        ----------
        '''
        ##first we check if we must use the cosmology
        if COSMO_conf['UseCo'].lower() == 'no':
            print('ok')
            MTU.Info('No cosmological constraints applied', 'No')
            self.Cosmo_templates = T_emline
            self.Cosmo_param = self.Parameter_array
 
        else:
            ##first we find the age position in the list of parameters
            Index_age = self.Names.index('age')
            ##this gives the row of the age in the parameter array

            ##then we must find all the column where age <= AgeUniverse
            ##WARNING!!! the age in the cosmo lib is given in Gyr while
            ##           for the template it is given in yr.

            Index_good_ages = numpy.where(self.Parameter_array.T[Index_age] \
                    <= Cosmo_obj['AgeUniverse']*10**9)[0] 

            ##compute the difference for information
            Dif = len(T_emline)-len(Index_good_ages)
            Left = len(T_emline)-Dif
            ##then select the right template
            Cosmo_templates = T_emline[Index_good_ages]
            ##and the right paramters
            Cosmo_param = self.Parameter_array[Index_good_ages]

            self.Cosmo_templates = Cosmo_templates
            self.Cosmo_param = Cosmo_param
 
    def prepare_lib_at_z(self, galaxy, COSMO):
        '''
        Take the Library and put it at the right redshift
        
        Parameter
        ---------
        galaxy      obj, galaxy we are fitting
        COSMO       dict, COSMO properties at the redshift
        
        Attributes
        ------
        Wave_at_z       1Darray, redshifted wavelength
        '''
        ### first we redshift the waves 
        self.Wave_at_z = numpy.array(self.Wave_final*(1+galaxy.Redshift))

        ## then we must redshift the fluxes. 
        ## WARNING: The models are in Lsolar.A^-1 therefore
        ## we must put them back in erg/s/AA (multiply by solar_lumino_erg_s)
        ## and Then we apply F(z [erg/s/cm2/AA]) = F(z=0, erg/s/AA) / (4 * pi * Dl^2 * (1+z)) 
        A = Phys_const().solar_lumino_erg_s() / (4*scipy.constants.pi*(COSMO['DL']**2)*(1+galaxy.Redshift))
        self.Temp_at_z = numpy.array(self.Cosmo_templates * A)



    def adjust_par_ext(self, DUST, IGM):
        '''
        Method that include the IGM and Dust values 
        into the library of parameters
        Parameters:
        -----------
        IGM         obj, IGM configuration
        DUST        obj, dust configuration

        New Attribute:
        --------------
        array_param  numpy array, (of zeros) of the size of all the
                                  parameters * all the template
        '''
        ##number of dust extinction curve to use
        ndust_curve = len(DUST.Dustfile_list)
        if ndust_curve != 0 and DUST.Dustfile_list[0] != 'none': 
            arraydust = self.param_dust(DUST) 
        else:
            arraydust = self.Cosmo_param
  
        ##number of IGM curve to use
        nigm_curve = len(IGM.dict['Curves'])
        if nigm_curve != 0:
            arrayigm = self.param_IGM(IGM, arraydust)
        else:
            arrayigm = arraydust

        ##and add it as attribute
        self.array_param = arrayigm

    def param_IGM(self, IGM, arraydust):
        '''
        This method adds the IGM parameters to the array
        of parameter from the parameter library where dust had been
        added already

        Parameter:
        ---------
        IGM         obj, IGM configuration
        arraydust   numpy.array, array of parameters with dust
        Return:
        -------
        array numpy array, parameter with igm added
        '''
        
        ###extract igm transmission
        Ntr = IGM.dict['Transmissions']

        ##number of IGM curves to be used
        if Ntr.size == 3:  ###one curve, 3 transmission
            Ncurve_igm = 1
        else:  #####Ncurve = 7; Ntr.size = 3; trans * 7curves = 21
            Ncurve_igm = len(Ntr)

        ##number of IGM template (alpha, beta, gamma transmissions)
        Npar_igm = 3

        ##number of templates and number of parameters
        ##already in the library
        ntemp, npar = arraydust.shape
    
        ###update the number of parameters
        npar_update = npar + Npar_igm

        ##create new array of parameter
        Ntemp_update =  ntemp * Ncurve_igm
        array_update  = numpy.zeros((Ntemp_update, npar_update))
        for i in range(Ncurve_igm):
            array_update[i*ntemp:(i+1)*ntemp, :npar] = arraydust 
        
        ##and add igm parameters
        ####add ebv values
        igms = numpy.empty((Ntemp_update, Npar_igm))
        for i in range(Ncurve_igm):
            if Ntr.size == 3:
                igms[i*ntemp : (i+1)*ntemp] = Ntr 
            else:
                igms[i*ntemp : (i+1)*ntemp] = Ntr[i] 

        ##and add it to the array of parameters
        array_update[:,npar:] = igms

        #for i in range(int(Ntemp_update/ntemp)):
            ###all these rows must be the same except 3 last columns
            #print(i*ntemp+300, i, ntemp, array_update[i*ntemp+300])  
 
        self.Names.append('TrLya')
        self.Names.append('TrLyb')
        self.Names.append('TrLyg')

        return array_update

    def param_dust(self, DUST):
        '''
        This method add the dust parameter to the array
        of parameter from the dust free parameter library

        Parameter:
        ---------
        DUST    obj, Dust configuration

        Return:
        -------
        Param_dust numpy array, parameter with dust added
        '''
        ##number of dust extinction curve to use
        ndust_curve = len(DUST.Dustfile_list)
        ##number of Ebv value to use for each curve
        ndust_values = len(DUST.values)      

        ##number of templates and number of parameters
        ##already in the library
        ntemp, npar = self.Cosmo_param.shape
        if ndust_curve != 0:
            ##1 for the curves and 1 for the ebv
            par_add = 1 #2        
             
        ###create new array
        NTEMP = ntemp*ndust_curve*ndust_values
        array  = numpy.zeros((NTEMP, npar+par_add))
        for i in range(int(NTEMP/ntemp)):
            array[i*ntemp:(i+1)*ntemp, :npar] = self.Cosmo_param 
        
        #for i in range(int(NTEMP/ntemp)):
        #    print(array[i*ntemp+300])  ###all these rows must be the same
        

        ####add curve identificator
        #curve_para = numpy.empty((NTEMP))  
        #for i in range(ndust_curve):
        #    curve_para[i*int(NTEMP/ndust_curve):(i+1)*int(NTEMP/ndust_curve)] = i

        #and add it to the array of parameter 
        #array.T[npar] = curve_para
 


        ####add ebv values
        ebvs = numpy.empty((NTEMP))
        N = 0
        for i in range(ndust_curve):
            for j in DUST.values:
                ebvs[N*ntemp:(N+1)*ntemp] = j
                N += 1

        ##and add it to the array of parameters
        array.T[npar] = ebvs

#        for i in range(int(NTEMP/ntemp)):
#            print(array[i*ntemp+300])  ###all these rows must be the same       
#        time.sleep(1000)

        #self.Names.append('Dust_curve')
        self.Names.append('EBV')
        return array


    def change_resolution(self, CONF, galaxy, template):
        '''
        This method adjust the resolution of the model to the resolution
        of the spectra.

        It can do it for one or multiple spectra.

        For data at a resolution of X (in Ang) and model at a resolution of Y (in Ang)
        we apply a gaussian filter to each template with a dispersion Z given by

        Z = sqrt(X*X - Z*Z)

        !!!!WARNING!!!!!
        This is applied IF AND ONLY IF the resolution of the data is smaller 
        than the one of the model

        Parameters:
        ----------
        Redshift            float, redshift of the observation
        CONF                dict, of the user configuration
        Template_emline     numpy.array, templates with emission lines
            
        Return
        ------
        '''
        ###new array initialization
        Template_res = numpy.copy(template)
        R = self.model_res(CONF.LIB['BaseSSP'])

        ###loop over each spectrum
        for s in galaxy.SPECS:
            ###wavelength of the observation
            wavespec = galaxy.SPECS[s][3]
            minw = min(wavespec)
            maxw = max(wavespec)
            middle = minw + (maxw-minw)/2

            ### index of the wavelength in the templates that correpond to the observed
            ## spectrum (we downgrade only the roight region). We take slightly
            ###larger to make sure
            index_min = (numpy.abs(self.Wave_final-minw/(1+galaxy.Redshift))).argmin()-1
            index_max = (numpy.abs(self.Wave_final-maxw/(1+galaxy.Redshift))).argmin()+1

            ###############we loop over the list of resolution
            ##number of different model resolution overlapping to the data
            N = 0  
            ###resolving power list
            Rlist = []
            for i in R:
                ##retrieve models resolution wavelenth limits
                minRw = i[1]
                maxRw = i[2]
                ##check if the spectra wavelengths are all in the range
                ##defined by minRw and maxRw
                if minw/(1+galaxy.Redshift)>minRw and maxw/(1+galaxy.Redshift)<maxRw:
                    #if this is the case we does not move anything
                    N = 'ok'
                    Rlist.append(i[0])
                else:
                    ##if it is not ok we increment N
                    N+=1
                    Rlist.append(i[0])


            if N == 'ok':
                ####we have only one resolution--> we downgrade everything

                #Resolving power of the models in the rest frame
                Res_mod = middle / (1+galaxy.Redshift) / Rlist[0]

                ##resolution of the data
                if CONF.CONF['NSpec'] == 1:
                    ResolvingPOwer = float(CONF.SPEC['Res'])
                else:
                    ResolvingPOwer = float(CONF.SPEC['Res'].split(';')[s-1])
                Res_rf_data = middle/ResolvingPOwer/(1+galaxy.Redshift)

                ##if the resolution of the models is lower than the one of the data
                ###we do not change the templates
                ##otherwise we have to downgrade them
                if Res_rf_data > Res_mod:
                    ###we have to smooth the templates
                    ###FWHM to sigma :
                    ratio = 2 * numpy.sqrt(2*numpy.log(2))
                    ###and compute the smooth (sigma of the gaussian filter)
                    smooth = numpy.sqrt((Res_rf_data)**2 - (Res_mod)**2)/ratio

                    ###here comes the 'trick'. My guess is that the gaussian_filter function
                    ###in scipy works well only if the grid of wavelength is binned with 1A
                    ###gaps. Tried with 20AA grid and everything was washed out.
                    ###therefore, here, for each template, we regrid the region of interest
                    ###to one angstrom, then we smooth it, and finally we re-regrid it to
                    ###the orginal grid---> might be faster way but this is that one for the
                    ###moment
                    waveset = self.Wave_final[index_min: index_max]
                    waveinterp = numpy.arange(self.Wave_final[index_min], self.Wave_final[index_max], 1)                    
                    for i in range(len(Template_res)):
                        temp = numpy.interp(waveinterp, waveset, Template_res[i][index_min:index_max])
                        smoothed = gaussian_filter(temp, smooth)
                        Template_res[i][index_min:index_max] = numpy.interp(waveset, waveinterp, \
                                smoothed)

        self.Template_res = Template_res


    def model_res(self, baseSSP):
        '''
        Method that give the resolution of the SSP chosen by the user

        The resolution is the median resolution of the full templates
        if there is one resolution only (like BC03 at low resolution)
        or a list of resolution if the resolution is varying drastically
        inside the template (like BC03 at high resolution)

        Parameter
        ---------
        baseSSP     str, of the baseSSP used by the user

        return
        ------
        R           list, of resolving power of the model with wavelength range
        '''

        if baseSSP[0:4] == 'BC03':
            #if we find LR in the name
            if baseSSP.find('LR') != -1:
                #1 zone to define
                R = [[300, 91, 160000]]

            #if we find HR in the name
            if baseSSP.find('HR') != -1:
                #3 zines to define
                R = [[300,91,3200], [2000,3200,9500] , [300, 9500, 16000]]


        return R

