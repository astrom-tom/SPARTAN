'''
The SPARTAN project
-------------------
Module that deals with Unit conversion
@author: R. THOMAS
@year  : 2016
@place : UV/LAM/UCBJ
'''
###Third party########
import scipy.constants
######################

class Phys_const:
    '''
    This class deals with the physical constants needed in SPARTAN
    '''
    def speed_of_light_ms(self,):
        '''
        Methods the return the speed of light in m/s
        ''' 
        return scipy.constants.c

    def solar_mass_kg(self,):
        '''
        Method that returns the solar mass in kilogrammes
        '''
        return 1.98e30

    def solar_lumino_erg_s(self,):
        '''
        Method that returns the solar luminosity in erg/s
        '''
        return 3.826e33

    def Planck_cst(self,):
        '''
        Method that return the planck constant in erg.s
        '''
        #### scipy gives:    h = 6.62607004e-34 J.s 
        #### and we have --> 1 erg = 1e-7 J
        ###         so h = scipy(h)*1e7 = 6.62607004e-27 erg.s
        return 1e7 * scipy.constants.h 

class length:
    '''
    This class deals with length unit conversion
    '''
    def __init__(self):
        '''
        class initialization, empty for the moment
        '''
        pass

    def m_to_cm(self, L):
        '''
        Method that converts meters to centimeters
        Parameter
        ---------
        L   float, lenth in meter
        '''
        return L*100.

    def cm_to_m(self, L):
        '''
        Method that converts meters to centimeters
        Parameter
        ---------
        L   float, lenth in centimeter
        '''
        return L/100.

    def pc_to_cm(self, L):
        '''
        Methods that converts parsec to centimeters
        Parameter
        ---------
        L   float, length in parsec
        '''
        return self.m_to_cm(self.pc_to_m(L))

    def pc_to_m(self, L):
        '''
        Method that converts parsec to meters
        Parameter
        ---------
        L   float, lenth in parsec
        '''
        return L*3.085e16

    def m_to_pc(self, L):
        '''
        Method that converts meters to parsecs
        Parameter
        ---------
        L   float, lenth in meter
        '''
        return L/(3.085e16)

    def mpc_to_m(self, L):
        '''
        Method that converts Mpc to meters
        Parameter
        ---------
        L   float, lenth in Mpc
        '''
        return L*3.085e22

    def m_to_mpc(self, L):
        '''
        Method that converts meters to Megaparsecs
        Parameter
        ---------
        L   float, lenth in meter
        '''
        return L/(3.085e22)

    def cm_to_mpc(self, L):
        '''
        Method that converts meters to parsecs
        Parameter
        ---------
        L   float, lenth in centimeter
        '''
        return L/(3.085e24)

    def mpc_to_cm(self, L):
        '''
        Method that converts meters to parsecs
        Parameter
        ---------
        L   float, lenth in centimeter
        '''
        return L*(3.085e24)

    def km_to_mpc(self, L):
        '''
        Method that converts meters to parsecs
        Parameter
        ---------
        L   float, lenth in centimeter
        '''
        return L*(3.2407e-20)


    def ang_to_m(self, L):
        '''
        Method that convert Ang to M
        Parameter
        ---------
        L   flt, wavelength in angstrom

        Return
        ------
        L   flt, wavelength in meter
        '''
        return L*1e-10

    def m_to_ang(self, L):
        '''
        Method that convert meters to angstroms
        Parameter
        ---------
        L   flt, wavelength in meter

        Return
        ------
        L   flt, wavelength in angstroms
        '''
        return L*1e10

    def ang_to_nm(self, L):
        '''
        Method that convert Angstrom to nanometer
        Parameter
        ---------
        L   flt, wavelength in angstrom

        Return
        ------
        L   flt, wavelength in nanometer
        '''
        return L*0.1

    def nm_to_ang(self, L):
        '''
        Method that convert nanometer to anstrom
        Parameter
        ---------
        L   flt, wavelength in nanometer

        Return
        ------
        L   flt, wavelength in angstrom
        '''
        return L*10

    def ang_to_mum(self, L):
        '''
        Method that convert Angstrom to micrometer
        Parameter
        ---------
        L   flt, wavelength in angstrom

        Return
        ------
        L   flt, wavelength in micrometer
        '''
        return L*1e-4

    def mum_to_ang(self, L):
        '''
        Method that convert micrometer to Angstrom
        Parameter
        ---------
        L   flt, wavelength in micrometer

        Return
        ------
        L   flt, wavelength in Angstrom
        '''
        return L*1e4

class time:
    def Gyr_to_sec(self, T):
        '''
        Method that convert sec to Gyr
        Parameter
        ---------
        T   flt, Time in sec

        Return
        ------
        T   flt, Time in Gyr
        '''
 
        return T*(3.15e16)
