'''
The SPARTAN project
-------------------
Module dealing with adding emission line to the library

@author: R. THOMAS
@year  : 2016-17 
@Place : UV/LAM/UCBJ/ESO
@License: GPL licence - see LICENCE.txt
'''

####Python Standard Libraries
import os
import warnings 
warnings.simplefilter(action='ignore', category=FutureWarning)
import time
########################

####Third party
import numpy
import h5py
from   scipy import interpolate
###########################

####SPARTAN moduls
from .input_spartan_files  import sp_input_files as PIF
from .units                import Phys_const, length
#from SPARTAN_plot_check.Check_plots import plot
##################################################

class Apply:
    '''
    This module deals with the emission line addition to the template
    during the fit
    '''
    def __init__(self, Library, CONF, toskip):
        '''
        Class initialization, retrieve input files for emission line
        treatment
        Parameters
        ----------
        Library     object, Library of template
        CONF        dict,   configuration of the user
        toskip      list of str, list of line names to be skipped

        '''
        Ratios, Neb_cont = PIF().emission_lines()
        self.Ratios = Ratios
        self.Neb_cont = Neb_cont
        self.Template = self.main(Library, CONF, toskip)


    def main(self, Library, CONF, toskip):
        '''
        This method is the main function that adds the emission lines
        Parameter:
        ---------
        Library     object, Library of template
        CONF            , dict of configuration
        toskip          , list of line to skip
        Return:
        -------
        Template_emline  ,Nd array of template flux with emission line (or original if
                          emission line are not applied)
        '''

        if CONF.LIB['EMline'].lower() == 'yes':
            ##initialize ionization edges
            wedge = self.init_edges()

            ##compute number of lyman continnuum photons
            LCP = self.NLym_cont_photons(wedge, Library.Wave_final, Library.Templates_final)
            #############################################
       
            ## Compute the nebular continuum Nebular continuum
            fgas = 1.0
            Nebular_cont = self.Nebular_continuum(LCP,fgas, Library.Wave_final, len(Library.Templates_final))
            ##############################################

            ###localize metallicity index
            for i in range(len(Library.Names)):
                if Library.Names[i]=='MET':
                    index = i
            #and create the metallicity array
            Metlist = numpy.zeros(len(Library.Templates_final))
            Met = Library.Parameter_array.T[index]
            for i in range(len(Metlist)):
                Metlist[i] = Met[i]
            ################################

            ###equivalent width and line flux computation
            EW, lumi, Name, lambdal, pos_line, l_line = self.EW_calcul(LCP, \
                    fgas, Metlist, Library.Wave_final, Library.Templates_final, Nebular_cont, toskip, CONF)

            ###and create the lines on the flux

            #-->old one #flux_emLINE = self.Em_line_on_template1(l_line, pos_line, Templates_final, \
            #        Nebular_cont, Wave_final, Metlist)

            flux_emLINE2 = self.Em_line_on_template2(l_line, pos_line, Library.Templates_final, \
                    Nebular_cont, Library.Wave_final, Metlist)

            #####################################
            ###check with plots
            #X = 10
            #print(Parameter_array[X])
            #plot().EmLinecheck(Wave_final, Templates_final[X], Nebular_cont[X], flux_emLINE[X])
            #print(Templates_final.shape, flux_emLINE.shape)
            return flux_emLINE2

        else:
            return Library.Templates_final
   

    def Em_line_on_template2(self, l_line, pos_line, flux, cont, wave, Metlist):
        '''
        This methods creates the emission line on the 
        template
        The line flux is added to the closest wavelength in
        the grid.

        Parameter
        ---------
        l_line      array, luminosity of each line
        pos_line    array, position of each line
        flux        array, flux of the templates
        cont        array, nebular continnuum 
        wave        array, wavelength grid

        Return
        ------
        '''

        i = 1

        flux_dirac = numpy.zeros( (len(flux), len(wave)))

        ###loop over spectrums and group lines which may be at adjacent positions.
        #We need to make sure that the continuum flux is maintained before and after the position
        #where the line is added! Otherwise several lines falling at neighbouring positions
        #will artificially create a broad (hence too strong) line. 

        
        Metunique = numpy.unique(Metlist)
        l_line2 = numpy.copy(l_line)
        pos_line2 = numpy.copy(pos_line)
        cont2 = numpy.copy(cont)
        flux2 = numpy.copy(flux)

        flux_dirac_arrays = []

        for k in Metunique:
            met_template = numpy.where(Metlist == k)[0]
            l_linemet = l_line2[met_template]
            pos_linemet = pos_line2[met_template]
            fluxmet = flux2[met_template]
            contmet = cont2[met_template]
            flux_dirac_met = numpy.zeros(l_linemet.shape)

            posi = numpy.where(pos_linemet[1] == 1)

            for j in range(len(pos_linemet[1])):
                if pos_linemet[1][j] == 1:

                    if pos_linemet[1][j-1] == 1:
                        l_linemet.T[j] = l_linemet.T[j] + l_linemet.T[j-1]
                        pos_linemet[1][j-1] = 0

                    if pos_linemet[1][j+1] == 1:
                        l_linemet.T[j] = l_linemet.T[j] + l_linemet.T[j-1]
                        pos_linemet[1][j-1] = 0
     
                    width = 0.5*abs(wave[j+1]-wave[j]) + 0.5*abs(wave[j]-wave[j-1])
                    fl_line = l_linemet.T[j] / width
                    
                    flux_dirac_met.T[j] = fluxmet.T[j]   + fl_line + contmet.T[j]

                else:

                    flux_dirac_met.T[j] = fluxmet.T[j] + contmet.T[j]
            flux_dirac_arrays.append(flux_dirac_met)

        fast = [ i for i in flux_dirac_arrays]
        F = numpy.concatenate(fast)
        return F
    
    def Em_line_on_template1(self, l_line, pos_line, flux, cont, wave, Metlist):

        '''
        This methods creates the emission line on the 
        template
        The line flux is added to the closest wavelength in
        the grid.

        Parameter
        ---------
        l_line      array, luminosity of each line
        pos_line    array, position of each line
        flux        array, flux of the templates
        cont        array, nebular continnuum 
        wave        array, wavelength grid

        Return
        ------
        '''


        flux_dirac = numpy.zeros( (len(flux), len(wave)))

        ###loop over spectrums and group lines which may be at adjacent positions.
        #We need to make sure that the continuum flux is maintained before and after the position
        #where the line is added! Otherwise several lines falling at neighbouring positions
        #will artificially create a broad (hence too strong) line. 

 

        t = time.time()
        for i in range(len(flux_dirac)):
            j = 1
            while j<len(wave)-1: 
                #if j!=0 and j!=len(wave):
                if pos_line[i][j] == 1:

                    if pos_line[i][j-1] == 1:
                        l_line[i][j] = l_line[i][j] + l_line[i][j-1]
                        pos_line[i][j-1] = 0

                    if pos_line[i][j+1] == 1:
                        l_line[i][j] = l_line[i][j] + l_line[i][j+1]
                        pos_line[i][j+1] = 0

                    width = 0.5*abs(wave[j+1]-wave[j]) + 0.5*abs(wave[j]  -wave[j-1])
                    fl_line = l_line[i][j] / width 
                    flux_dirac[i][j] = flux[i][j]   + fl_line + cont[i][j]

                else:

                    flux_dirac[i][j] = flux[i][j]+cont[i][j]

                j+=1



        return flux_dirac

    def init_edges(self):
        '''
        Initialises ionisation edges

        Parameters:
        ----------
        NONE

        Returns:
        -------
        wedge   array, wavelength list with ionisation edge in Ang
        '''
        wedge = 1.e+8 / 109678.758e+0  #H edge in Angstroem   =911.75AA 
                                          #    ground state (B-X)  
        return wedge 


    def NLym_cont_photons(self, wedge, wave, flux):
        '''
        Calculate the number of continuum photons shortward of ionising edges.

        Parameters:
        ----------
        wave    array, of wave from the SED in angstrom 
        flux    array, of flux from the SED in erg.s-1.A-1
        wedge   array, containing wavelength of edges [A]

        Returns:
        -------
        qi   array, array containing nedge ionising fluxes 
                         [#photons s^-1]
        '''

        ###
        qi = 0

        ###
        qsum  = numpy.zeros(len(flux))
        i     = 1  #2
 
        ### Planck cst in erg.s
        h = Phys_const().Planck_cst()  
        ##light speed in ang/s
        c = length().m_to_ang(Phys_const().speed_of_light_ms())

        while wave[i] <= wedge:
            ###trapz integration
            qsum = qsum + (flux.T[i]+flux.T[i-1])*0.5*(wave[i]-wave[i-1])*wave[i]/(h*c)
            qi=qsum
            i+=1
       
        return qi

    def Nebular_continuum(self, q0, fgas, wave, Ntemp):
        '''
        Calculates the nebular continuous emission

        Assumes electron temperature Te=10000 K, n(HeII)/n(HI) = 0.1
        and n(HeIII)/n(HI) = 0.

        Parameters:
        ----------
        q0:    number of Lyman continuum photons per second
        fgas:  fraction of Lyman cont.photons which is absorbed by gaz
              (rest assumed to be lost)
        wsed:  wavelength grid to calculate nebular emission [A]

        Returns:
        -------
        flux_neb: nebular flux in [ergs s^-1 A^-1] 
                    (on wavelength grid given by wave)
        '''

        ###CSt
        alpha_2 = 2.575e-13 # [cm^3 s^-1] total recombination coeff. for hydrogen for Te=10000 K 
                            # (except to groundstate)
        xn_hep  = 0.1       # n(HeII)/n(HI
       
        ##extract emission coefficient from file
        ga_h, ga_2q, ga_hei, wave_emc = numpy.loadtxt(self.Neb_cont).T
        new_wave_emc = wave

        ##interpolation ovewr the SED's wave grid 
        ga_h_interp = numpy.interp(new_wave_emc,wave_emc,ga_h)
        ga_2q_interp = numpy.interp(new_wave_emc, wave_emc, ga_2q) 
        ga_hei_interp = numpy.interp(new_wave_emc, wave_emc, ga_hei)
       
        ##Cst
        c = length().m_to_ang(Phys_const().speed_of_light_ms())
        ### the emission line coef are in 1e-40 erg.cm^3.s^-1.Hz^-1
        Factor = c*1e-40

        ##compute emission
        flux_nebular = []
        for i in range(len(wave)):
            a = numpy.where(new_wave_emc==wave[i]) 
            add_h = ga_h_interp[a]
            add_2q = ga_2q_interp[a]
            add_hei = ga_hei_interp[a]
            ga_tot = (add_h + add_2q + xn_hep * add_hei)
            ## all the coefficient are in 1e-40 erg/cm3/s/Hz,to put it back
            ## in erg/s/cm2/AA we use lFl=vFv --> Fl = c/l^2 * Fv 
            ## with c=2.9979 e18 AA/s
            fluxneb_i  = Factor*ga_tot/alpha_2/(wave[i]*wave[i])
            fluxneb_i  = fluxneb_i[0] * fgas  # *q0 but this is done below  
                                              ###this is in erg/cm2/s/A (q0 in cm-2.s-1)
            flux_nebular.append(fluxneb_i)

        ###multiply by q0[i] and save it
        Neb_cont_lib = numpy.zeros((Ntemp,len(wave)))
        '''
        t = time.time()
        for i in range(len(Neb_cont_lib)):
            for j in range(len(Neb_cont_lib.T)):
                Neb_cont_lib[i][j] = flux_nebular[j]*q0[i]
        '''
        ##above was the first version (two nested loops), replaced later by list comprehension (30% faster)
        Neb_cont_lib = numpy.array([[flux_nebular[j]*q0[i] for j in range(len(Neb_cont_lib.T))] for i in range(len(Neb_cont_lib)) ])

        return Neb_cont_lib


    def skipline(self, toskip, CONF):
        '''
        This method loop over the list of emission line and remove the one that
        have to be skipped

        Parameters
        ----------
        toskip      list, of emission l ine to skip
        CONF        dict, configuration of the user

        Returns
        ------
        Nameskip    list, name of line that we keep
        lambdaskip   '' , wavelength '' '' 
        Z1skip       '' , ratio for Z1   ''
        Z2skip       '' ,   ''      Z2   ''
        Z35skip       '' ,   ''      Z35   ''
        '''

        Name, lambdal, Z1, Z2, Z35 = numpy.genfromtxt(self.Ratios, dtype='str').T
        lambdal = lambdal.astype('float')
        Z1 = Z1.astype('float')
        Z2 = Z2.astype('float')
        Z35 = Z35.astype('float')

        line_to_skip = CONF.LIB['Emline_skipped'].split(';') 
        Nameskip = []
        lambdalskip = []
        Z1skip = []
        Z2skip = []
        Z35skip = []

        for i in range(len(Name)):
            if (Name[i] not in toskip) and (Name[i] not in line_to_skip) :
                Nameskip.append(Name[i])
                lambdalskip.append(lambdal[i])
                Z1skip.append(Z1[i])
                Z2skip.append(Z2[i])
                Z35skip.append(Z35[i])

        return Nameskip, lambdalskip, Z1skip, Z2skip, Z35skip


    def EW_calcul(self, q0, fgas, metal, wave, flux, cont, toskip, CONF):
        '''
        Calculates the line luminosity and equivalent widths of nebular lines 
        and adds the corresponding flux to the spectrum at the 
        appropriate position.
        Note: to preserve correctly the total line flux this routine
              assumes that the trapezium rule is used when computing 
              the flux in different filters (see filter routine). 

        Parameter
        ---------
        q0:     float, number of Lyman continuum photons per second
        fgas:   float, fraction of Lyman cont.photons which is absorbed by gas (rest assumed to be lost)
        metal:  float, metallicity [in solar units] used to select different empirical line ratios
        wave:   array, wavelength grid of continuum 
        flux:   array, original continuum flux grid
        cont    array, nebular continuum 
        toskip  list, of line to skip
        Output:
        ------
        flux: at output the line flux is added to 'flux'
        ew_line: array with EW's
        f_line: array with line fluxes
        '''

        ###H_beta luminosity assuming Case B, Te=10000-K
        l_ref = 4.77e-13*q0*fgas
        
        #####extract line ratios
        ###first we check if some line have to be skept
        Name, lambdal, Z1, Z2, Z35 = self.skipline(toskip, CONF)
        ratio = [Z1, Z2, Z35]
       
        ###metal stuff
        metal_array = [0.02, 0.2, 0.4]
        #             1/50, 1/5, >1/2.5  in Zsolar units --> 1=Zsun     

        ##we check the values of the template and replace for high values
        metal_emLine = numpy.zeros(len(metal))
        for i in range(len(metal)):
            if metal[i] >= 0.4:
                metal_emLine[i] = 0.4
            else:
                metal_emLine[i] = metal[i]

        ##luminosity and EW array
        EW = numpy.zeros((len(metal), len(Name) ))
        lumi = numpy.zeros((len(metal), len(Name) ))

        ##initialize arrays
        ratio_line = numpy.zeros((len(metal), len(Name)))
        i_line = numpy.zeros((len(metal),len(wave)))
        l_line = numpy.zeros((len(metal),len(wave)))
      
        ####for Lya and Ha (see below)
        WWL = [1190.0, 1240.0]
        AA =    interpolate.interp1d(wave, flux+cont)(WWL)
        WWH = [6510.0, 6610.0]
        BB =    interpolate.interp1d(wave, flux+cont)(WWH)

        ###find position of lines
        pos = list(numpy.zeros(len(wave)))
        name_index_wave = []
        for j in range(len(Name)):
            rec_wave = lambdal[j] 
            ##find the place in the SED-s wavelength grid
            index_wave = self.find_pos(rec_wave, wave)
            name_index_wave.append(index_wave)
            ##save the index in the position
            pos[index_wave] = Name[j]

        for i in range(len(i_line)):
            id_pos = pos
            for j in range(len(Name)):
                index_wave = name_index_wave[j]

                for k in range(len(metal_array)):
                    if metal_array[k] == metal_emLine[i]:
                        ratio_line[i][j] = ratio[k][j]

                ##compute line luminosity
                l_line[i][index_wave] = l_line[i][index_wave] + l_ref[i]*ratio_line[i][j]
                ## signal a line at this position
                i_line[i][index_wave] = 1

                if Name[j] == 'H_Lya':
                    ##Special treatment --> Ly-a: absorption can be strong
                    ##need of different cont. point
                    central_cont = self.interpvalue(lambdal[j], WWL, AA[i])
                    ewi = l_line[i][index_wave] / central_cont
                    flinei = l_line[i][index_wave]

                elif Name[j] == 'H_alpha':
                    ##idem
                    central_cont = self.interpvalue(lambdal[j], WWH, BB[i])
                    ewi = l_line[i][index_wave] / central_cont 
                    flinei = l_line[i][index_wave]

                else:
                    ewi = l_line[i][index_wave] / (flux[i][index_wave]+cont[i][index_wave])
                    flinei = l_line[i][index_wave]

                ###save line flux and EW
                EW[i][j] = ewi
                lumi[i][j] = flinei

        return EW, lumi, Name, lambdal, i_line, l_line  

    def interpvalue(self, X, wave, flux):
        '''
        Find the value of flux(X)

        Parameter
        ---------
        X       float, wave where we want the value of X
        wave    array, SED's wave grid
        flux    array, flux of the SED
        '''
        new_wave = numpy.round(numpy.arange(wave[0], wave[-1]+1, 1),2)
        new_flux = numpy.interp(new_wave, wave, flux)
        a = numpy.where(new_wave==float(X))
        return new_flux[a][0]


    def find_pos(self, lambda_line, waveSED):
        '''
        This methods finds the position (index) of the line
        in the wavelength grid of the SED. It looks for the nearest 
        wavelength.

        Parameter
        ---------
        lambda_line     float, wavelength in Ang of the line
        wave            array, wavelength grid of the SED
        '''
        ##we substract the wavelength of the line to all the 
        ##wavelength of the grid and we keep the index of
        ##the smallest difference.
        index_i = (numpy.abs(waveSED-lambda_line)).argmin()

        return index_i

    
