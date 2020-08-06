'''
The SPARTAN Project
-------------------
This module fits the spectroscopy alone over the library

@author: R. THOMAS
@year: 2016
@place: UV/LAM/UCBJ
@License: GPL v3.0 - see LICENCE.txt
'''
#---------------------------------------------------------------------
###Python standard library
import sys
import os
import time
import multiprocessing
###############################

###third party#####################
import tqdm
import numpy
numpy.set_printoptions(threshold=sys.maxsize)
import copy
import scipy.interpolate as interp
###################################

##Local Modules#########################################
from .cosmo     import Cosmology as cosmo
from .          import Data_for_fit as data
from .          import messages as MTU
from .          import Lib_common as Lib
from .          import Lib_Emission_line as Emline
from .          import Lib_extinction as extinction
from .          import photometry_prepare_photo_fit as photo_fit
from .          import photometry_Compute_photo as Comp_phot
from .          import spectroscopy_clean_regions as cleaning
from .          import spectroscopy_emission_lines_first_guesses as lines
from .units     import Phys_const
from .          import length
from .          import Data_for_fit
from .          import Results_file_save as save
from .          import Results_Cat_final as Cat
#############################################################
######
from .          import plot_specfit
from .          import plot_clean
from .          import plot_specfit as plotfit


#----------------------------------------------------------------------
class Fit_spectro:
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
        

        ##prepare dust extinction
        MTU.Info('Preparation of the Dust extinction', 'No')
        DUST  = extinction.Dust(self.CONF, Library.Wave_final) 

        ##We open the datafile to extract ID list and Nobj
        MTU.Info('Checking sample to fit (might take a while)', 'No')
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
                Toparallel.append((k, objs[k], copy.deepcopy(Library), DUST, self.CONF, \
                        self.Datafile, COSMOS, len(sample)))

            ##3-And start parallel processing
            timebefore_loop = time.time()
            pool = multiprocessing.Pool(processes = len(Toparallel))
            Results_pool=pool.map(self.fit, Toparallel)
            pool.close()
            pool.join()
            timeafter_loop = time.time()

            ##4-Now we save the results
            MTU.Info('Now we Save results!', 'No')
            for gal in Results_pool:
                if gal.status == 'Fitted':
                    save.save_spec(self.Resfile, gal, self.CONF)
                    MTU.Info('Object %s: %s'%(gal.ID, gal.status), 'No')
                else:
                    MTU.Error('Object %s could not be fitted: %s' %(gal.ID,  gal.status), 'No')
                    save.save_to_file_fail(self.Resfile, gal, self.CONF)
            MTU.Info('the %s objects were fitted in %s seconds'%(int(self.CONF.CONF['NCPU']),\
                    timeafter_loop-timebefore_loop), 'Yes')

            if len(sample)-i >= 0:
                MTU.Info('%s objects left'%(len(sample)-i), 'No')
        MTU.Info('Full sample fitted in %s seconds'%( time.time() - Time_INITIAL), 'Yes')
        MTU.Info('Start creation of the final catalog', 'Yes')
        Cat.final(self.CONF, self.Resfile)


    def fit(self, run): 
        '''
        Fitting function. It takes a pack
        '''
        try:
            ##unpack
            k, spec, lib, DUST, CONF, Datafile, COSMOS, Nobj = run

            ###start time counting####
            fit_start = time.time()

            ###################################
            ###        Initialization       ###
            ###################################
            ##we retrieve the data for the object
            galaxy = Data_for_fit.indiv_obj(Datafile, spec, 'spec', CONF)

            ####################################
            ###  edges and BR cleaning #########
            ####################################
            galaxy_copy = copy.deepcopy(galaxy)
            cleaning.main(galaxy, CONF)
            #plot_clean.cleaning_plot(galaxy_copy, galaxy)

            ###################################
            ###     Photometry ################
            ###################################
            Photofit = photo_fit.Photo_for_fit(CONF.PHOT['Photo_config'], 0, 'spec')
            Photofit.match(galaxy)
            Photofit.extract_from_data(Photofit.allbands)

            ####################################
            ###     Check redshift           ###
            ####################################
            if galaxy.Redshift <= 0 : 
                galaxy.status =  'Negative or null Redshift'
                return galaxy
     
            ##we have to add the emission lines to the templates
            ##But first we look if some have to be skipped or 
            ##some are not detected in the spectra
            lines_to_skip = lines.check(galaxy, self.CONF.LIB['Emline_skipped'].split(';'))
            ##then we add the list to the one given by the user
            all_lines_to_skip = lines_to_skip + \
                    [l.strip() for l in self.CONF.LIB['Emline_skipped'].split(';')]

            ###and finally add the emission lines to the templates
            MTU.Info('Addition of Emission line', 'No')
            Template_emLine = Emline.Apply(lib, self.CONF, all_lines_to_skip).Template

            #####################################
            ###### Adjust spectral Resolution ###
            #####################################
            lib.change_resolution(CONF, galaxy, Template_emLine)

            ######################################
            ###### Retrieve IGM Inform  ##########
            ######################################
            ### We check if we will use some IGM and if Yes, we prepare it
            IGM = extinction.IGMlib(CONF, galaxy, lib)

            #####################################
            ##### Adjust for cosmology ##########
            #####################################
            COSMO_obj = {'AgeUniverse':COSMOS.Age_Universe(galaxy.Redshift),  \
                             'DL':length.mpc_to_cm(COSMOS.dl(galaxy.Redshift))}
            lib.Make_cosmological_Lib(COSMO_obj, lib.Template_res, CONF.COSMO)
            ntemp = len(lib.Cosmo_templates)

            ###and redshift the whole library
            lib.prepare_lib_at_z(galaxy, COSMO_obj) 

            ####################################
            ######final parameter array########
            ####################################
            lib.adjust_par_ext(DUST, IGM)
            NTEMP = len(lib.array_param)

            #####################################
            ##### Term Communication ############
            #####################################
            MTU.Info('We start to fit object with ID %s'%(galaxy.ID), 'Yes')
            MTU.Info('Redshift: %s '%galaxy.Redshift, 'No')
            MTU.Info('Number of templates (!No extinction applied): %s'%ntemp, 'No')
            MTU.Info('Number of templates with all extinctions: %s' %NTEMP, 'No')
            MTU.Info('Start fitting!', 'No')

            ####################################
            ######## start the fit #############
            ####################################
            ###innitialize array
            CHI2array = numpy.zeros((NTEMP))
            Normarray = numpy.zeros((NTEMP))
            galaxy.bestchi2red = 1e20
            galaxy.template_wave = lib.Wave_at_z

            n = 0 

            if DUST.use == 'Yes' and IGM.dict['Use'] == 'Yes':
                for i in range(len(DUST.Dustfile_list)): 
                    curve = DUST.coef[i]
                    for igm in IGM.dict['Curves']:
                        temp_with_igm = IGM.Make_IGM_library(lib.Temp_at_z, \
                                    igm, lib.Wave_at_z)
                        for ebv in DUST.values:
                            temp_with_ext = DUST.Make_dusted_template(temp_with_igm, curve, ebv)
                            ##and process them
                            CHI2, Norm, Flux_mag_all_template, regrid_template, index_chi, waveobs =\
                                    self.process_template(lib, Photofit, temp_with_ext, galaxy)
                            ##populate arrays
                            CHI2min = CHI2[index_chi]
                            CHI2array[n*ntemp:(n+1)*ntemp] = CHI2
                            Normarray[n*ntemp:(n+1)*ntemp] = Norm 
                            if len(CHI2min)>1:
                                CHI2min = CHI2min[0]
                            ##update the results
                            if CHI2min<galaxy.bestchi2red:
                                #print(CHI2min, galaxy.bestchi2red)
                                galaxy.best_chi2(numpy.min(CHI2), \
                                        temp_with_ext[index_chi][0]*Norm[index_chi][0], \
                                        regrid_template[index_chi], Flux_mag_all_template.T[index_chi],\
                                        [lib.Wave_at_z, waveobs], n*ntemp + index_chi[0], 'spec')
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
                        CHI2, Norm, Flux_mag_all_template, regrid_template, index_chi, waveobs =\
                                self.process_template(lib, Photofit, temp_with_ext, galaxy)
                        ##populate arrays
                        CHI2min = CHI2[index_chi]
                        CHI2array[n*ntemp:(n+1)*ntemp] = CHI2
                        Normarray[n*ntemp:(n+1)*ntemp] = Norm 
                        if len(CHI2min)>1:
                            CHI2min = CHI2min[0]
     
                        ##update the results
                        if CHI2min<galaxy.bestchi2red:
                            #print(CHI2min, galaxy.bestchi2red)
                            galaxy.best_chi2(numpy.min(CHI2), \
                                    temp_with_ext[index_chi][0]*Norm[index_chi][0], \
                                    regrid_template[index_chi], Flux_mag_all_template.T[index_chi],\
                                    [lib.Wave_at_z, waveobs], n*ntemp + index_chi[0], 'spec')
                            galaxy.Bf_param(lib, Norm[index_chi][0])
                        n += 1
         
            if DUST.use == 'No' and IGM.dict['Use'] == 'Yes':
                for igm in IGM.dict['Curves']:
                    ###apply IGM
                    temp_with_ext = IGM.Make_IGM_library(lib.Temp_at_z, igm, lib.Wave_at_z)
                    ##and process them
                    CHI2, Norm, Flux_mag_all_template, regrid_template, index_chi, waveobs =\
                            self.process_template(lib, Photofit, temp_with_ext, galaxy)
                    ##populate arrays
                    CHI2min = CHI2[index_chi]
                    CHI2array[n*ntemp:(n+1)*ntemp] = CHI2
                    Normarray[n*ntemp:(n+1)*ntemp] = Norm 
                    if len(CHI2min)>1:
                        CHI2min = CHI2min[0]
     
                    ##update the results
                    if CHI2min<galaxy.bestchi2red:
                        #print(CHI2min, galaxy.bestchi2red)
                        galaxy.best_chi2(numpy.min(CHI2), \
                                temp_with_ext[index_chi][0]*Norm[index_chi][0], \
                                regrid_template[index_chi], Flux_mag_all_template.T[index_chi],\
                                [lib.Wave_at_z, waveobs], n*ntemp + index_chi[0], 'spec')
                        galaxy.Bf_param(lib, Norm[index_chi][0])
                    n += 1

            elif DUST.use == 'No' and IGM.dict['Use'] == 'No':
                ###no extinction is used, we go directly with the 'naked'
                ###library of template
                temp_with_ext = lib.Temp_at_z
                ##and process them
                #M_final, Norm, Flux_mag_all_template, CHI2, index_chi \
                CHI2, Norm, Flux_mag_all_template, regrid_template, index_chi, waveobs =\
                        self.process_template(lib, Photofit, temp_with_ext, galaxy)
                ##populate arrays
                CHI2min = CHI2[index_chi]
                CHI2array[n*ntemp:(n+1)*ntemp] = CHI2
                Normarray[n*ntemp:(n+1)*ntemp] = Norm 
                if len(CHI2min)>1:
                    CHI2min = CHI2min[0]
     
                ##update the results
                if CHI2min<galaxy.bestchi2red:
                    #print(CHI2min, galaxy.bestchi2red)
                    galaxy.best_chi2(numpy.min(CHI2), \
                            temp_with_ext[index_chi][0]*Norm[index_chi][0], \
                            regrid_template[index_chi], Flux_mag_all_template.T[index_chi],\
                            [lib.Wave_at_z, waveobs], n*ntemp + index_chi[0], 'spec')
                    galaxy.Bf_param(lib, Norm[index_chi][0])
                n += 1
            
            if 'BFparam' not in list(galaxy.__dict__.keys()):
                galaxy.status = 'FAIL'
                return  galaxy

            ####instead of taking the probability from the chi2
            ####we subtract the chi2min. 
            ###the resulting PDF_final will just be equal
            ###to constant*true_PDF which will not change the
            ###error and measurement estimates
            scales = numpy.array(CHI2array) - min(CHI2array)

            P_CHI2 = []
            #for k in range(len(scales)):
            #    P_CHI2.append(numpy.exp(-(scales[k])/2))

            P_CHI2 = numpy.exp(-(scales)/2)
     
            galaxy.create_observable_spec(Photofit) 
            galaxy.chi2param(lib, numpy.array(P_CHI2), Normarray, CONF)
            galaxy.status = 'Fitted'

            ###########on the fly visualisation
            #plot_specfit.specfit(galaxy.besttemplate_wave, galaxy.besttemplate, galaxy.regrid_template \
            #         ,galaxy.SPECS)
     
            fit_end = time.time()
            MTU.Info('Galaxy %s fitted in %s seconds'%(galaxy.ID, fit_end-fit_start), 'No')

            return galaxy

        except:

            galaxy.status = 'No evident reason could be found'
            return galaxy

    def process_template(self, lib, Photofit, temp_with_ext, galaxy):
        '''
        Function that normalize all the template and compute
        the magnitude in each band.
        Parameters:
        -----------
        lib             obj, libreary of template
        galaxy          obj, galaxy object containing the normalisation information 
        temp_with_ext   numpy array, template chunk with all extinctions applied
        Photofit        obj, with photometric configuration

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
        #print(temp_with_ext[0])
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
        Flux_mag_all_template = Norm.T * temp_with_ext.T
    
        ##then we must regrid the template over the template grid
        wavef = []
        fluxsf = []
        errsf = []
        for i in galaxy.SPECS.keys():
            wavef.append(galaxy.SPECS[i][3])  
            fluxsf.append(galaxy.SPECS[i][4])
            errsf.append(galaxy.SPECS[i][5])
        waves = numpy.concatenate(wavef)
        fluxs = numpy.concatenate(fluxsf)
        errs = numpy.concatenate(errsf)
        regrid_templates = interp.interp1d(lib.Wave_at_z, Flux_mag_all_template.T)(waves)

        ##We compute the CHI2 
        CHI2 =  numpy.sum((fluxs - regrid_templates)**2    / errs**2, axis=1) 
        #print(CHI2)
        ##and find the minimum    
        index_chi  = numpy.where(CHI2 == numpy.min(CHI2))
        
        return  CHI2, Norm, Flux_mag_all_template, regrid_templates, index_chi, waves
