'''
The SPARTAN Project
-------------------
Modul dealing with the preparation of photometry for the fit
in SPARTAN

@Author R. THOMAS
@year   2016-18
@place  UV/LAM/UCBJ/ESO
@License: GPL v3.0 licence - see LICENCE.txt
'''

####Third party##
import numpy
import scipy
#################

###Local imports###################################################
from .input_spartan_files import sp_input_files as PIF
from .units               import Phys_const, length
from .                    import photometry_filters as filters
from .                    import photometry_Compute_photo as Compute
#####################################################################

class Photo_for_fit:
    '''
    Class preparing the photometry
    '''
    def __init__(self, photo_conf, Nskip, typedata):
        '''
        Initialization of the class
        Parameters:
        -----------
        indiv_obj	obj, galaxies we are fitting
        photo_conf	dict, photometrc configuration of the user
        Nskip		dict, number of photometric point to skip in the list
                                          (--> when combined fit, we skip the points use for
                                                        spectroscopy)

        Attributes:
        -----------
        photo_conf	
        Nskip
        '''
        self.Nskip = Nskip
        self.photo_conf = photo_conf
        self.typedata = typedata

    def match(self, galaxy):
        '''
        This makes the match between photometry of a given object
        and the photometric configuration
        Parameter
        ---------
        galaxy      obj, galaxy to be fitted (attribute, mags and redshift)
        '''

        self.good_bands = []
        self.upper_limits = []
        self.allbands = []
        self.Nnorm = 0

        ####in case of combined fit we created two magnitudes
        ####attributes --> we have to choose the right one
        if self.typedata == 'mag': 
            toiterate = galaxy.Magnitudes
        else:
            toiterate = galaxy.Magnitudes_spec
            #print(self.photo_conf)

        for b in range(len(toiterate)):
            if b>=self.Nskip:
                band = toiterate[b]
                #### If the band as a physical measurement:
                if float(band[1]) > 0:
                    #we create a dictionnary for each band
                    band_dict = {}
                    ##with the measurement
                    band_dict['Meas'] = float(band[1])
                    ##the error
                    band_dict['err'] = float(band[2])
                    ##if we have a rectangular filter
                    if band[0][0] == 'door':
                        band_dict['name'] = 'door'
                        band_dict['Filter'] = 'rectangle'
                        band_dict['Fit'] = 'yes'
                        band_dict['Out'] = 'yes'
                        band_dict['Abs'] = 'yes'
                        band_dict['Fit'] = 'yes'
                        band_dict['Norm'] = 'yes' 
                        filt = filters.Retrieve_Filter_inf() 
                        Tran = filt.rectangular(band[0][1], band[0][2])
                        Tran = Tran['Tran']
                        ##and add it to the dict
                        band_dict['Tran'] = Tran
                        band_dict['Flux'] = Compute.mag2flux(float(band[1]), Tran[2])
                        band_dict['Fluxerr'] = 0.4*numpy.log(10)*Compute.mag2flux(float(band[1]),\
                                    Tran[2])*band_dict['err']
                            ##finally we add the dict to the list of good filters
                        self.good_bands.append(band_dict)
                        self.allbands.append(band_dict)

                    ##if we have a normal filter
                    else:
                        band_dict['name'] = band[0]
                        ##and then we look at the configuration
                        k = 0
                        for j in self.photo_conf:
                            ##of the current filter
                            if j['name'] == band_dict['name'] and k >= self.Nskip:
                                ##and add the configuration to the dictionary
                                band_dict['Filter'] = j['Filter']
                                band_dict['Fit'] = j['Fit']
                                band_dict['Out'] = j['Out']
                                band_dict['Abs'] = j['Abs']
                                band_dict['Fit'] = j['Fit']
                                band_dict['Norm'] = j['Nor']
                                break
                            k += 1

                        if band_dict['Fit'] == 'yes':
                            ### if the configuration says we use this filter
                            ### we go to retrieve the filter informations
                            filt = filters.Retrieve_Filter_inf() 
                            Tran = filt.retrieve_one_filter(band_dict['Filter'])
                            ##and add it to the dict
                            band_dict['Tran'] = Tran
                            band_dict['Flux'] = Compute.mag2flux(float(band[1]), Tran[2])
                            band_dict['Fluxerr'] = 0.4*numpy.log(10)*Compute.mag2flux(float(band[1]),\
                                Tran[2])*band_dict['err']

                            ##finally we add the dict to the list of good filters
                            if band_dict['err'] == -1.0:
                                #or Tran[2]/(1+galaxy.Redshift)<912:
                                self.upper_limits.append(band_dict['name'])
                            else:
                                self.good_bands.append(band_dict['name'])
                                
                            ###and to the allband 
                            self.allbands.append(band_dict)

                        if band_dict['Norm'] == 'yes':
                            if  band_dict['err'] < 0:
                                band_dict['Norm'] = 'no'
                            else:
                                self.Nnorm += 1
            

    def extract_from_data(self, bands):
        '''
        Extract fluxes and error from data

        Paramters:
        ---------
        bands   list, of bands dictionnaries, see photometric configuration for details

        Return:
        ------
        BANDS           list of 2 lists, 1-flux, 2-fluxerr
        Leff_all_bands  list of effective wavelength
        '''
        flux_all_bands = []
        fluxerr_all_bands = []
        Leff_all_bands = []
        Norm_index = []
        Norm_flux = []
        Names = []
        Meas = []
        err = []
        for i in range(len(bands)):
            Leff_all_bands.append(bands[i]['Tran'][2])
            flux_all_bands.append(bands[i]['Flux'])
            fluxerr_all_bands.append(bands[i]['Fluxerr'])
            Names.append(bands[i]['name'])
            Meas.append(bands[i]['Meas'])
            err.append(bands[i]['err'])
            if bands[i]['Norm'] == 'yes':
                Norm_index.append(i)
                Norm_flux.append(bands[i]['Flux'])

        ##convert them to numpy arrays
        self.flux_all_bands    = numpy.array(flux_all_bands)
        self.fluxerr_all_bands = numpy.array(fluxerr_all_bands)
        self.Leff_all_bands    = numpy.array(Leff_all_bands)
        self.Norm_index        = numpy.array(Norm_index)
        self.Norm_flux         = numpy.array(Norm_flux)
        self.Meas              = numpy.array(Meas)
        self.err               = numpy.array(err)
        self.Names             = numpy.array(Names)

