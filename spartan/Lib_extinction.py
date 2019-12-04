'''
The SPARTAN project
-------------------
Module dealing with extinctions during the fit

@author: R. THOMAS
@year  : 2016 
@Place : UV/LAM/UCBJ
@License: CeCILL-v2 licence - see LICENCE.txt
'''

####Python Standard Libraries
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
###############################

####Third party###################
import numpy
import h5py
from   scipy import interpolate
import matplotlib.pyplot as plt
######################################

####Local Modules#########################
from .input_spartan_files import sp_input_files as PIF
from .                    import messages as MTU
from .                    import plot_specfit as plotigm
from .units               import Phys_const, length
#import check_plots.igmapplied as plotigm
############################################

#---------------------------------------------------------------------
class Dust:
    '''
    Dust Preparation for the fit
    '''
    def __init__(self, CONF, wavelength):
        '''
        class creation, 
        Parameter:
        ----------
        CONF        dict, configuration of the user
        wavelength  numpy array, wavelength of the templates

        Attributes:
        -----------
        values      numpy array, of EBV values
        use         str, yes or no to use the dust extinction during the fit
        coef        numpy array, extinction coefficient (regrided to the wavelenght
                                    of the template)
        '''

        self.Dustfile_list = [self.Dust_conf(CONF)]
        self.values = numpy.array(CONF.LIB['EBVList'].split(';')).astype('float')
        self.use, self.coef = self.Dust_for_fit(self.Dustfile_list, wavelength, self.values)


    def Dust_conf(self, CONF):
        '''
        Method that go to find the Dustfile to use during the fit
        (if specified by the user)

        Parameter:
        ---------
        config  dict, configuration of the fit from user

        Return:
        ------
        DUSTfile   str, /path/to/extinction curve file
        '''
        ##retrieve input directory
        Input_dir = PIF().inputdir
        ##and dust curve name from the user
        Dust_curve = CONF.LIB['DustUse']
        ##localize the file
        if Dust_curve != 'none':
            DUSTfile = os.path.join(Input_dir, 'EXT/%s.dat'%Dust_curve)
        else:
            DUSTfile = 'none'
        return DUSTfile


    def Dust_for_fit(self, Dustfile, wave_models, EBVlist):
        '''
        Method that prepares the final extinction curve to be used
        during the fit
        Parameter
        ---------
        Dustfile    str, /path/to/extinction curve file
        wave_model  1D array, wavelength of the templates
        EBVlist     list of str, list of EBV values given by tthe user
        Return
        ------
        Dust_for_fit 2D array, with wavelength in the first clumn and 
                               extinction coefficient in the second
        '''
        if Dustfile[0] == 'none':
            DUSTuse = 'No'
            DUSTcoeff = []
        else:
            DUSTcoeff = []
            for i in Dustfile:
                ##1- We extract the extinction curve
                WaveDust, CoefDust = numpy.loadtxt(i).T
                ##2- Then we regrid to the model 
                DUSTuse = 'Yes'
                DUSTcoeff.append(numpy.interp(wave_models, WaveDust, CoefDust)) 

        return  DUSTuse, DUSTcoeff 

    def Make_dusted_template(self, template, dustcurve, ebv):
        '''
        This method combines the free dust template and the dust extinction 

        Parameter
        ---------
        Template    1d array, templates flux
        dustcurve    1d array, dustcurve to be used
        ebv         float, abv value to apply

        Return
        ------
        New_template_dust   1darray, template with extinction
        '''
        Dust_trans = self.Dust_ext(ebv, dustcurve)
        return Dust_trans * template
   
    def Dust_ext(self, ebv, Coef):
        '''
        Method that compute the coefficient from the extinction anf the EBV value
        Parameter
        ---------
        ebv     float, E(B-V) value given by the user
        Coef    1D array, extinction coefficient regridded to the wave model grid (restframe)

        Return
        ------
        Dust_trans  1Darray, of the dust transmission computed as 10**(-0.4*E(B-V)*k(lambda))
                    See http://webast.ast.obs-mip.fr/hyperz/hyperz_manual1/node10.html for detail
        '''
        Dust_trans = 10**(-0.4*ebv*Coef)
        return Dust_trans

class IGMlib:
    '''
    Class preparing the IGM for the fit
    '''
    def __init__(self, CONF, galaxy, Library):
        '''
        Initialization of the IGM. Selects the IGM to be used

        Parameter:
        ---------
        config  dict, configuration of the fit from user
        galaxy  obj, galaxy we are fitting
        Library obj, Library properties

        Attributes:
        -----------
        IGMfile     str, IGM file to be used
        typeIGM     str, IGM type (free or mean)
        '''

        ##retrieve Input directory
        Input_dir = PIF().inputdir
        ##and IGM Type given by the user
        IGMtype = CONF.LIB['IGMtype']
        ##then takes the file
        if IGMtype.lower() == 'none' or galaxy.Redshift < 1.5:
            IGMfile = 'none'
            typeIGM = 'none' 
        elif IGMtype == 'mean_meiksin':
            IGMfile = os.path.join(Input_dir, 'IGM/SPARTAN_Meiksin_Free_7curves.hdf5')
            typeIGM = 'mean'
        elif IGMtype == 'mean_madau':
            IGMfile = os.path.join(Input_dir, 'IGM/SPARTAN_Madau_Free_7curves.hdf5')
            typeIGM = 'mean'
        elif IGMtype == 'free_meiksin':
            IGMfile = os.path.join(Input_dir, 'IGM/SPARTAN_Meiksin_Free_7curves.hdf5')
            #IGMfile = os.path.join(Input_dir, 'IGM/SPARTAN_Meiksin_Free_mega.hdf5')
            typeIGM = 'free'
        elif IGMtype == 'free_madau':
            IGMfile = os.path.join(Input_dir, 'IGM/SPARTAN_Madau_Free_7curves.hdf5')
            typeIGM = 'free'

        self.file = IGMfile
        self.type = typeIGM
        self.IGM_for_fit(galaxy, Library)

    def IGM_for_fit(self, galaxy, Library):
        '''
        Method that make gives out the IGM dictionnary for the fit
        Parameter
        ---------
        galaxy      object, galaxy we are fitting
        Library     object, Library of model

        Attributes
        ----------
        IGM_dict    dict, information about the IGM to use during the fit
        '''
       	IGM_dict = {}
        if self.file == 'none' or galaxy.Redshift<1.5:
            IGM_dict['Use'] = 'No'
            IGM_dict['Curves'] = []
        else:
            IGM_dict['Use'] = 'Yes'
            IGM_dict['Curves'], IGM_dict['Transmissions']\
                    = self.take_curve(galaxy.Redshift, Library.Wave_final) 

        self.dict= IGM_dict

    def take_curve(self, redshift, wave_model):
        '''
        Method that prepares the IGM for the fit. It selects
        the right curve(s) and regrid them to the wavelength grid of the models
        Parameter
        ---------
        redshift    float, redshift of the object
        wave_model  1D array, restframe wavelength of the models

        Return
        ------
        To_Use      list, of each curve interpolated to the wave_model grid
        '''
        To_Use = []
        ###here we round the redshift to 4 digits
        ###the IGM templates are not more details (and it 
        ###is probably useless to give more than 4 digits)
        redshift = round(redshift,4)
        ## Open the IGMfile
        with h5py.File(self.file, 'r') as IGM:
            Curves = numpy.array(IGM['%s/Curve'%str(redshift)])
            Wave = numpy.array(IGM['Wavelength/Wave'])
            Tr = numpy.array(IGM['%s/Transmissions'%str(redshift)])

        #print(Wave, wave_model)
        if self.type == 'free':
            ##if the user uses the free prescription
            ## so 5
            for i in range(len(Curves)):
                ###to avoid the fact where the normalization is done in
                ###an igm part where the transmission is at 0 we replace
                ###the 0s be 1e-10
                Curves[Curves==0] = 1e-10
                ##we interpolate each curve to the model grid
                ##and add it to To_Use with the transmissions
                To_Use.append(numpy.interp(wave_model, Wave, Curves[i]))
        
        if self.type == 'mean':
            ##if the user uses the mean prescription we need to extract the 
            ##mean curve
            ##we interpolate the curve to the model grid
            ##and add it to To_Use with the transmissions
            To_Use.append(numpy.interp(wave_model, Wave, Curves[3]))
            Tr = Tr[3]
            
        return To_Use, Tr

    def Make_IGM_library(self, templates, igmcurve, wave):
        '''
        Methods that applies the IGM to the library
        Parameter
        ---------
        templates       numpy array, with template flux
        igmcurve        numpy array (1D), with igm curve
        
        Return
        ------
        igmtemplates    numpy.array, with igm-applied templates
        '''
        
        #plotigm.igm(wave, igmcurve)        
        igmtemplates = templates * igmcurve
        return igmtemplates

