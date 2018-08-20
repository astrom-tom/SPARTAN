'''
The SPARTAN Project
-------------------
This module fits the photometry over the library

@author: R. THOMAS
@year: 2016-18
@place: UV/LAM/UCBJ
@License: GPL v3.0 - see LICENCE.txt
'''
#---------------------------------------------------------------------
###Python standard
import sys
import os
import time
import multiprocessing
import copy
####################

###third party#####
import numpy
import tqdm
import matplotlib.pyplot as plt
####################

##Local Modules########################
from .cosmo           import Cosmology as cosmo
from .                import Data_for_fit as data
from .                import messages as MTU
from .                import Lib_common as Lib
from .                import Lib_Emission_line as Emline
from .                import Lib_extinction as extinction
from .                import photometry_prepare_photo_fit as photo_fit
from .                import photometry_Compute_photo as Comp_phot
from .units           import Phys_const
from .                import length
from .                import Data_for_fit
from .                import Results_file_save as save
from .                import Results_Cat_final as Cat
#from check_plots.photofit import photofit as plot
########################################


class Fit_photo:
    '''
    Photometric fitting
    '''
    def __init__(self, CONF):
        '''
        class creation defines run attributes
        '''
        ##Datafile
        self.Datafile = os.path.join(CONF.CONF['PDir'], '%s_dat.hdf5'%CONF.CONF['PName'])

        ##Result files
        self.Resfile = os.path.join(CONF.CONF['PDir'], '%s_Res.hdf5'%CONF.CONF['PName'])
        self.Resfile_off = os.path.join(CONF.CONF['PDir'], '%s_Res_offset.hdf5'%CONF.CONF['PName'])

        ##Library file
        self.LIBfile = os.path.join(CONF.CONF['PDir'], '%s_LIB.hdf5'%CONF.CONF['PName'])

        ###FULL CONF
        self.CONF = CONF


    def main(self):
        '''
        Main function of the photometric fitting

        Parameter:
        ---------
        Return:
        ------
        '''
        #Prepare cosmology module
        #first extract cosmological parameters from user config
        Ho = float(self.CONF.COSMO['Ho'])
        Omega_m = float(self.CONF.COSMO['Omega_m'])
        Omega_L = float(self.CONF.COSMO['Omega_L'])
        ##then prepare the module
        MTU.Info('Prepare cosmology module....Done', 'Yes')
        COSMOS = cosmo(Ho, Omega_m, Omega_L)

        ##Initialize time
        Time_INITIAL = time.time()

        ###Instentiate the library 
        MTU.Info('Extract the library', 'No')
        Library = Lib.LIB(self.LIBfile)
        
        ##we first add the emission lines to the templates
        MTU.Info('Addition of Emission line', 'No')
        Templates_emLine = Emline.Apply(Library, self.CONF, toskip = []).Template


        ##prepare dust extinction
        MTU.Info('Preparation of the Dust extinction', 'No')
        DUST  = extinction.Dust(self.CONF, Library.Wave_final) 

        ##We open the datafile to extract ID list and Nobj
        sample = Data_for_fit.sample_to_fit(self.Datafile, self.Resfile, self.CONF.FIT['OverFit'])

        ##start the main loop
        i = 0
        N = 1
        while i < len(sample):
            #1-select Ncpu object
            MTU.Info('Start Parallel Fit of NCPU = %s objects'%int(self.CONF.CONF['NCPU']), 'Yes')
            objs = sample[i:i+N*int(self.CONF.CONF['NCPU'])]
            i+=N*int(self.CONF.CONF['NCPU'])
            Observed_chunks = [objs[j:j+N] for j in range(0, len(objs), N)] 

            ##2-We prepare each part
            Toparallel = []
            for k in range(len(Observed_chunks)):
                Toparallel.append((k, objs[k], copy.deepcopy(Library), Templates_emLine,  \
                        DUST, self.CONF, self.Datafile, COSMOS, len(sample)))

            ##3-And start parallel processing
            timebefore_loop = time.time()
            pool = multiprocessing.Pool(processes = len(Toparallel))
            Results_pool=pool.map(self.fit, Toparallel)
            pool.close()
            pool.join()
            timeafter_loop = time.time()
            #sys.exit()

            ##4-Now we save the results
            MTU.Info('Now we Save results!', 'No')
            for gal in Results_pool:
                if gal.status == 'Fitted':
                    save.save_phot(self.Resfile, gal, self.CONF)
                    MTU.Info('Object %s: %s'%(gal.ID, gal.status), 'No')
                else:
                    MTU.Error('Object %s could not be fitted: %s' %(gal.ID,  gal.status), 'No')
                    save.save_to_file_fail(self.Resfile, gal, self.CONF.FIT['OverFit'])

            MTU.Info('the %s objects were fitted in %s seconds'%(int(self.CONF.CONF['NCPU']),\
                    timeafter_loop-timebefore_loop), 'Yes')

            if len(sample)-i >= 0:
                MTU.Info('%s objects left'%(len(sample)-i), 'No')


        MTU.Info('Full sample fitted in %s seconds'%( time.time() - Time_INITIAL), 'Yes')
        MTU.Info('Start creation of the final catalog', 'Yes')
        Cat.final(self.CONF, self.Resfile)
    



    def fit(self, run): 
        '''
        Fitting function. It takes a pack in arguments containing:
        k
        photo
        lib
        template_emline
        DUST
        CONF
        Datafile
        COSMOS
        Nobj
        '''
        k, photo, lib, Template_emLine,  DUST, CONF, Datafile, COSMOS, Nobj = run
           
        ###start time counting####
        fit_start = time.time()

        ###################################
        ###        Initialization       ###
        ###################################
        ##we retrieve the data for the object
        galaxy = Data_for_fit.indiv_obj(Datafile, photo, 'mag', CONF)

        try:

            ###################################
            ##      Photometry              ###
            ###################################
            ##check how many valid photometric points and keep the right ones
            ## and match photometric sample (for this object) with the set
            ## of photometric points
            Photofit = photo_fit.Photo_for_fit(CONF.PHOT['Photo_config'], 0, 'mag')
            ###and create the final photometric configuration Photofit.Final_band_array
            Photofit.match(galaxy)
            Photofit.extract_from_data(Photofit.allbands)
            ##check if in the good bands we have at least one normalisation band available
            if Photofit.Nnorm == 0:
                galaxy.status =  'no normalisation band'
                return galaxy

            ####################################
            ###     Check redshift           ###
            ####################################
            ###check the redshift
            if galaxy.Redshift <= 0 : 
                galaxy.status =  'Negative or null Redshift'
                return galaxy

            ######################################
            ###### Retrieve IGM Inform  ##########
            ######################################
            ### We check if we will use some IGM and if Yes, we prepare it
            IGM= extinction.IGMlib(CONF, galaxy, lib)
            
            #####################################
            ##### Adjust for cosmology ##########
            #####################################
            COSMO_obj = {'AgeUniverse':COSMOS.Age_Universe(galaxy.Redshift),  \
                             'DL':length.mpc_to_cm(COSMOS.dl(galaxy.Redshift))}
            lib.Make_cosmological_Lib(COSMO_obj, Template_emLine, CONF.COSMO)
            ntemp = len(lib.Cosmo_templates)

            ###and redshift the whole library
            lib.prepare_lib_at_z(galaxy, COSMO_obj) 

            ####################################
            ######final parameter array########
            ####################################
            lib.adjust_par_ext(DUST, IGM)
            #print(lib.array_param.shape)
            #print(lib.array_param[:,7:].shape, lib.array_param[:,7:][9000])
            #numpy.save('param_v1.npy', lib.array_param)
            NTEMP = len(lib.array_param)

            #####################################
            ##### Term Communication ############
            #####################################
            MTU.Info('We start to fit object with ID %s'%(galaxy.ID), 'Yes')
            MTU.Info('Total Number of bands: %s '%len(Photofit.allbands), 'No')
            MTU.Info('Number of good bands: %s '%len(Photofit.good_bands), 'No')
            MTU.Info('%s band(s) will be treated as upper limits'%len(Photofit.upper_limits), 'No')
            MTU.Info('We found %s bands for normalisation'%Photofit.Nnorm, 'No')
            MTU.Info('Redshift: %s '%galaxy.Redshift, 'No')
            MTU.Info('Number of templates (!No extinction applied): %s'%ntemp, 'No')
            MTU.Info('Number of templates with all extinctions: %s' %NTEMP, 'No')
            MTU.Info('Start fitting!', 'No')
            ####################################
            ######## start the fit #############
            ####################################


            ###innitialize array
            CHI2array = numpy.zeros((NTEMP))
            Probarray = numpy.zeros((NTEMP))
            Normarray = numpy.zeros((NTEMP))
            galaxy.bestchi2red = 1e10
            galaxy.template_wave = lib.Wave_at_z
            n = 0 

            if DUST.use == 'Yes' and IGM.dict['Use'] == 'Yes':
                for i in range(len(DUST.Dustfile_list)): 
                    curve = DUST.coef[i]
                    for igm in IGM.dict['Curves']:
                        temp_with_igm = IGM.Make_IGM_library(lib.Temp_at_z, \
                                    igm, lib.Wave_at_z)
     
                        for ebv in DUST.values:
                            temp_with_ext = DUST.Make_dusted_template(temp_with_igm,curve,ebv)

                            ##and process them
                            M_final, Norm, Flux_mag_all_template, CHI2, index_chi \
                                = self.process_template(lib, Photofit, temp_with_ext)

                            ##populate arrays
                            CHI2min = CHI2[index_chi]
                            CHI2array[n*ntemp:(n+1)*ntemp] = CHI2
                            Normarray[n*ntemp:(n+1)*ntemp] = Norm 
                            ##update the results
                            if CHI2min<galaxy.bestchi2red:
                                galaxy.best_chi2(numpy.min(CHI2), \
                                        temp_with_ext[index_chi][0]*Norm[index_chi][0], \
                                        M_final.T[index_chi], Flux_mag_all_template.T[index_chi],\
                                        lib.Wave_at_z, n*ntemp + index_chi[0], 'mag')
                                galaxy.Bf_param(lib, Norm[index_chi][0])

                            n += 1

            elif DUST.use == 'Yes' and IGM.dict['Use'] == 'No':     
                for i in range(len(DUST.Dustfile_list)):
                    ###extract curve
                    curve = DUST.coef[i]
                    for ebv in DUST.values:
                        ###apply the extinction
                        temp_with_ext = DUST.Make_dusted_template(lib.Temp_at_z,curve,ebv)       

                        ##and process them
                        M_final, Norm, Flux_mag_all_template, CHI2, index_chi \
                                = self.process_template(lib, Photofit, temp_with_ext)
                        
                        ##populate arrays
                        CHI2min = CHI2[index_chi]
                        CHI2array[n*ntemp:(n+1)*ntemp] = CHI2
                        Probarray[n*ntemp:(n+1)*ntemp] = numpy.exp(-CHI2/2)
                        Normarray[n*ntemp:(n+1)*ntemp] = Norm 
                        ##update the results
                        if CHI2min<galaxy.bestchi2red:

                            galaxy.best_chi2(numpy.min(CHI2), \
                                    temp_with_ext[index_chi][0]*Norm[index_chi][0], \
                                    M_final.T[index_chi], Flux_mag_all_template.T[index_chi],\
                                    lib.Wave_at_z, n*ntemp + index_chi[0], 'mag')

                            galaxy.Bf_param(lib, Norm[index_chi][0])

                        n += 1

            if DUST.use == 'No' and IGM.dict['Use'] == 'Yes':
                for igm in IGM.dict['Curves']:
                    ###apply IGM
                    temp_with_ext = IGM.Make_IGM_library(lib.Temp_at_z, igm, lib.Wave_at_z)

                    ##and process them
                    M_final, Norm, Flux_mag_all_template, CHI2, index_chi \
                            = self.process_template(lib, Photofit, temp_with_ext)
                    
                    ##populate arrays
                    CHI2min = CHI2[index_chi]
                    CHI2array[n*ntemp:(n+1)*ntemp] = CHI2
                    Probarray[n*ntemp:(n+1)*ntemp] = numpy.exp(-CHI2/2)
                    Normarray[n*ntemp:(n+1)*ntemp] = Norm 
                    ##update the results
                    if CHI2min<galaxy.bestchi2red:
                        galaxy.best_chi2(numpy.min(CHI2), \
                                temp_with_ext[index_chi][0]*Norm[index_chi][0], \
                                M_final.T[index_chi], Flux_mag_all_template.T[index_chi],\
                                lib.Wave_at_z, n*ntemp + index_chi[0], 'mag')

                        galaxy.Bf_param(lib, Norm[index_chi][0])
                    
                    n += 1
        
            if DUST.use == 'No' and IGM.dict['Use'] == 'No':
                    ###no extinction is used, we go directly with the 'naked'
                    ###library of template
                    temp_with_ext = lib.Temp_at_z
                    M_final, Norm, Flux_mag_all_template, CHI2, index_chi \
                            = self.process_template(lib, Photofit, lib.Temp_at_z)

                    ##populate arrays
                    CHI2min = CHI2[index_chi]
                    CHI2array[n*ntemp:(n+1)*ntemp] = CHI2
                    Probarray[n*ntemp:(n+1)*ntemp] = numpy.exp(-CHI2/2)
                    Normarray[n*ntemp:(n+1)*ntemp] = Norm 
                    ##update the results
                    if CHI2min<galaxy.bestchi2red:
                        galaxy.best_chi2(numpy.min(CHI2), \
                                temp_with_ext[index_chi][0]*Norm[index_chi][0], \
                                M_final.T[index_chi], Flux_mag_all_template.T[index_chi],\
                                lib.Wave_at_z, n*ntemp + index_chi[0], 'mag')

                        galaxy.Bf_param(lib, Norm[index_chi][0])

                    n += 1
        
            if 'BFparam' not in list(galaxy.__dict__.keys()):
                galaxy.status = 'FAIL'
                return  galaxy
            numpy.save('CHI2v1.npy',CHI2array)
            galaxy.create_observable(Photofit, fit_type='mag') 
            galaxy.chi2param(lib, CHI2array, Normarray, CONF)
            galaxy.magabs(CONF.PHOT['Photo_config'], COSMO_obj)
            galaxy.status = 'Fitted'
            #plot(galaxy.template_wave, galaxy.besttemplate, \
            #       galaxy.waveband, galaxy.obsflux, galaxy.bestfit_flux, galaxy.ID)

            fit_end = time.time()
            MTU.Info('Galaxy %s fitted in %s seconds'%(galaxy.ID, fit_end-fit_start), 'No')
            return galaxy
        except:
            galaxy.status = 'No evident resaon could be found'
            return galaxy


    def process_template(self, lib, Photofit, temp_with_ext):
        '''
        Function that normalize all the template and compute
        the magnitude in each band.
        Parameters:
        -----------
        lib         obj, libreary of template
        Photofit    obj, photometric data to fit
        temp_with_ext   numpy array, template chunk with all extinctions applied

        Return:
        -------
        M_final             numpy array, of normalized magnitude
        Norm                    ''     , of nromalisation (1 for each template)
        Flux_mag_all_template   ''     , template flux normalized
        CHI                     ''     , of chi2 (1 for each tempalte)
        index_chi               int    , index of the best template in M_final
        '''

        ###  we convert the array of templates, in erg/s/cm2/AA
        ##    to erg/s/cm2/Hz
        freqTemp, Templates_hz = Comp_phot.convert_wave_to_freq(lib.Wave_at_z, temp_with_ext)
        ## We normalize the templates to the observed photometry
        ## Then we must compute the normalisation bands from the redshifted template
        
        F_to_normalize, M_to_normalize = Comp_phot.array_template_to_phot_init(Photofit.allbands,\
                Templates_hz, lib.Wave_at_z, freqTemp)

        ## Then we must compare it with the observed bands! 
        Bands_for_norm = F_to_normalize[Photofit.Norm_index]
        for l in range(len(Photofit.Norm_index)):
            Bands_for_norm[l] = Photofit.Norm_flux[l] / Bands_for_norm[l]

        # then we make the mean of the normalisation for each template
        Norm = numpy.sum(Bands_for_norm, axis=0) / len(Photofit.Norm_index) 

        ## and multiply all the bands by the normalisation
        Flux_mag_all_template = Norm.T * F_to_normalize

        ###and look for upper limits template
        index_flux, index_temp = self.upper_limits_templates(Photofit, Flux_mag_all_template)
        #Norm = Norm [index_temp]
        M_to_normalize = M_to_normalize[index_flux].T
        #M_to_normalize = M_to_normalize.T[index_temp]
        
        ##Compute back the magnitudes
        M_final = M_to_normalize - 2.5*numpy.log10(Norm[index_flux])
        

        ###if there are some infinity value we replace them by NaNs
        M_final[M_final == numpy.inf] = numpy.nan
        

        ##We make the Chi2
        CHI2 = numpy.nansum( (Photofit.flux_all_bands[index_flux] - Flux_mag_all_template[index_flux].T)**2 / \
                Photofit.fluxerr_all_bands[index_flux]**2, axis = 1) 

        ###all the template that must be removed
        ###due to upper limits contraints have a chi2
        ### equal to NaN
        for i in index_temp:
            CHI2[i] = numpy.nan

        index_chi  = numpy.where(CHI2 == numpy.min(CHI2))
        return  M_final.T, Norm, Flux_mag_all_template, CHI2, index_chi


    def upper_limits_templates(self, Photofit, Flux_magnitude_temp):
        '''
        This method check if upper limits have found. If yes
        we compare templates magnitudes in each upper limit pass
        band. If the flux of the template is higher than the observed
        flux, then the template is discarded 

        Parameters:
        ----------
        Photofit                obj, photometric configuration
        Flux_magnitude_temp     numpy array, of normalised flux magnitudes

        Returns:
        --------
        index_bands_to_use_for_fit  list of ints, of index of the bands to use
                                          for the fit
        
        index_array                 list of arrays, each arrrays contain the index of the 
                                                    templates that will be removed from the
                                                    fit
        '''
        index_bands_to_use_for_fit = list(range(len(Photofit.allbands)))
        index_bands_upper = []
        index_arrays = []

        if len(Photofit.upper_limits)==0:
            return index_bands_to_use_for_fit, index_arrays

        else:
            #index_bands_to_use_for_fit = []

            for i in Photofit.upper_limits:
                index_upper = numpy.where(i == Photofit.Names)
                index_bands_to_use_for_fit.remove(index_upper[0][0])
                index_bands_upper.append(index_upper[0][0])
                flux = Photofit.flux_all_bands[index_upper]
                ####wh check which templates have a flux higher than the upper limits
                rows  = numpy.where(Flux_magnitude_temp[index_upper,:] > flux)
                index_arrays.append(rows[2])
        
            
            return index_bands_to_use_for_fit, index_arrays
