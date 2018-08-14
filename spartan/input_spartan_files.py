'''
The SPARTAN Project
-------------------
This file retrieve all the input files needed for SPARTAN

@author: R. THOMAS
@year: 2016-2017
@place: UV/LAM/UCBJ/ESO
@License: GPL v3.0 - see LICENCE.txt

Copyright (C) 2016 - 2017 Romain THOMAS

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
##### Python General Libraries
import os
from pathlib import Path

##third parties
import numpy

class sp_input_files:
    """
    This class centralize all the input files of SPARTAN
    """
    def __init__(self):
        """
        Class construction,
        Gives the directory of the input files of SPARTAN.
        It is define by the user after the installation in SPARTAN.conf in the
        root directory
        """

        home = str(Path.home())
        fileconf = os.path.join(home, '.spartan_conf')
        self.inputdir = numpy.genfromtxt(fileconf,dtype='str')[1]

    def template_conf(self):
        '''
        This method provides the Template SPARTAN configuration file
        '''
        return os.path.join(self.inputdir, 'SPARTAN_config_template.cfg')

    def Base_LibP(self):
        '''
        This method provides the list of SSP bases provided by SPARTAN
        '''
        return os.path.join(self.inputdir, 'LIBS/Lib_SPARTAN.txt')

    def Dust(self):
        '''
        This method provides the list of dust prescription provided by SPARTAN
        '''
        return os.path.join(self.inputdir, 'EXT/Dust_SPARTAN.txt')

    def filter(self):
        '''
        This method provides the filter file of SPARTAN
        '''
        return os.path.join(self.inputdir, 'SPARTAN_filters.hdf5')
    
    def photo_z(self):
        '''
        This method provides the photo-z optimized library of SPARTAN
        '''
        return os.path.join(self.inputdir, 'Red_LIB/photo-z_5_3990.hdf5')

    def emission_lines(self):
        '''
        This method provides the input files for the emission line treatment
        '''
        ####Line ratio table
        Ratios = os.path.join(self.inputdir, 'EmLine/Anders_Fritze_2003.dat')
        Neb_cont = os.path.join(self.inputdir, 'EmLine/Emission_coef.txt')

        return Ratios, Neb_cont

    def emission_line_compute(self):
        '''
        This method retrieve the file (that can be edited by the user) that
        lists the emission line that SPARTAN will compute
        '''
        EL_compute = os.path.join(self.inputdir, 'EmLine/EL_est.txt')
        return EL_compute
   
