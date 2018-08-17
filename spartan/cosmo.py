'''
The SPARTAN SIM Project
-------------------

Cosmology module. 

based on paper from David W. Hogg, 2000

@Author: R. THOMAS
@Place:  UV/LAM/ESO
@Year:   2016-17
@License: GPL v3.0 - see LICENCE.txt
'''
###Python third party###############
import numpy
from scipy import integrate
######################################

##local modules########################
from .units import Phys_const, length, time
########################################


class Cosmology:    
    '''
    Cosmology module
    '''
    def __init__(self, Ho, Omega_m, Omega_L): 
        '''
        Class construction 
        '''
        ### attributes of the class
        self.Ho = Ho         
        self.Omega_m = Omega_m
        self.Omega_L = Omega_L
        self.Omega_k = 0
        #### speed of light, m/s and conversion
        self.c = Phys_const().speed_of_light_ms()
        self.km_to_mpc = length().km_to_mpc(1)
        self.Gyr_to_sec = time().Gyr_to_sec(1)

    def Hubbletime(self, ):
        '''
        Method that computes the Hubble time
        Parameter:
        ----------
        z       flt, redshift

        Return
        ------
        tH      flt, Hubble time
        '''
        tH = 1/(self.Ho*self.km_to_mpc)
        return tH

    def Hubbledistance(self, ):
        '''
        Method that computes the Hubble distance
        Parameter:
        ----------
        z       flt, redshift

        Return
        ------
        dH      flt, Hubble time
        '''

        dH = self.c/(self.Ho*self.km_to_mpc)
        return dH


    def E(self, z):
        '''
        Method that computes the term E(z)
        Parameter:
        ----------
        z       flt, redshift

        Return
        ------
        E(w)      flt, E at z
        '''

        return numpy.sqrt(self.Omega_m*(1+z)**3 + self.Omega_k*(1+z)**2 + self.Omega_L)


    def H(self, z):
        '''
        Method that computes the hubble parameter at a given redshift
        Parameter:
        ---------
        z   float, redshift

        Return:
        -------
        H   float, Hubble parameter in m/s/Mpc
        '''
        H = self.Ho * self.E(z)
        
        return H

    def Age_Universe(self, z):
        '''
        Module that computes the age of the universe at a given redshift
        Parameter
        ---------
        z   float, redshift
        Return
        ------
        A   float, age of the universe at z in Gyr
        '''
        A_int= lambda x: 1/((1+x)*self.E(x))
        Age_un=integrate.quad(A_int,z,numpy.inf) 

        A=self.Hubbletime()*Age_un[0]/self.Gyr_to_sec

        return A


    def dc(self,z):
        '''
        Module that computes the comobile distance at z
        Parameter
        --------
        z   float, redshift
        Return
        ------
        dist_co float, comoving distance at z in Mpc
        '''

        D_int = lambda x: 1/self.E(x)
        Dc_in = integrate.quad(D_int,0,z)
        co_dist = self.Hubbledistance()*Dc_in[0] * self.km_to_mpc * 1e-3 ##to meter

        return co_dist 

    def dl(self, z):
        '''
        Method that compute luminosity distance at z
        Parameter
        ----------
        z   float, redshift
        Return
        ------
        dl  float, luminosity distance at redshift z, in Mpc
        '''
        ##compute dl, from dc
        da=(1/(1+z))*self.dc(z)
        dl=(1+z)*(1+z)*da

        return dl 

    def da(self, z):
        '''
        Method that computes the angular distance at redshift z
        Parameter
        ---------
        z   float, redshift
        Return
        ------
        da  float, angular distance at z in Mpc
        '''

        ##compute da from dc
        da=(1/(1+z))*self.dc(z)

        return da
