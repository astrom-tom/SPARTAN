'''
The SPARTAN Project
-------------------
Modul dealing with the filters in SPARTAN

@Author R. THOMAS
@year   2016
@place  UV/LAM/UCBJ
@License: GPL v3.0 licence - see LICENCE.txt
'''

####Third party####
import h5py
import numpy
###################

###Local imports
from .input_spartan_files         import sp_input_files as PIF
from .units                       import Phys_const, length

class Retrieve_Filter_inf:
    """
    This class deals with action that need to retrieve
    a filter name or to get filter data
    It implements 3 methods:
    """

    def __init__(self):
        """
        Class Constructor defining one attributes:

        self. Filterfile    The location of the filter file, and the file
        """
        self.Filterfile = PIF().filter()

    def filter_list(self):
        """
        Function that extract the filter name list from the filter file

        Parameter
        --------
        NONE    We use self.Filterfile from the constructor


        Return
        ------
        Fillist list of filter names. A name as the following format
                ==> filter-system

        """""
        ###First we load the filter
        filters = h5py.File(self.Filterfile, 'r')
        Filterlist = []
        for i in filters:
            ## 'i' is the group
            for j in filters[i]:
                ## 'j' is an object in the group
                Filterlist.append(j)
        ##then we close the file
        filters.close()
        
        return Filterlist

    def retrieve_one_filter(self, band_name):
        '''
        Method that retrieves the filter information for
        a given filter name
        Parameter
        ---------
        band_name   str, name of the band

        Return
        ------
        to_take     list, of 2 1D-array, wavelenght then throughput
        '''
        to_take = []
        with h5py.File(self.Filterfile, 'r') as allfilt:
            for i in allfilt:
                for j in allfilt[i]:
                    if j == band_name:
                        Filter = allfilt['%s/%s'%(i, band_name)]
                        to_take.append(Filter[0])
                        to_take.append(Filter[1])
                        to_take.append(self.compute_Lambda_eff_Filt(Filter[0], Filter[1]))
        return to_take

    def rectangular(self, l0, lf):
        '''
        This method creates a rectangular filter between l0 and lf
        IN THE OBSERVER FRAME
        Parameter
        ---------
        l0  float, first wavelength of the filter
        lf  float, last  wavelength of the filter
        '''
        ##create the filter 
        wavelength = numpy.arange(l0-20, lf+21)                
        throughput = []
        for i in range(len(wavelength)):
            if l0 < wavelength[i] < lf:
                throughput.append(1.)
            else:
                throughput.append(0.)

        ##compute effective wavelength
        Leff = self.compute_Lambda_eff_Filt(wavelength, throughput)

        band = {}
        band['Tran'] = [wavelength, throughput, Leff]
       
        return band


    def compute_Lambda_eff_Filt(self, Lambda, throughput):
        '''
        This modules compute the effective wavelength of the filter
        Parameter
        ---------
        Lambda      1Darray, wavelengths of the filter
        thoughput   1Darray, thoughtput of the filter
       
        Return
        ------
        Leff        float, effective wavelength of the filter
        '''
        ### we follow http://www.bdnyc.org/2013/07/filter-effective-wavelengths/
        A = numpy.trapz(Lambda * throughput, Lambda)   
        B = numpy.trapz(throughput, Lambda)

        Leff = A / B
        return Leff
