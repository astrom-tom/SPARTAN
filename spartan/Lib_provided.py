'''
###########################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
#####   Filter - Related
#####       operation
#####
###########################
@License: GPL licence - see LICENCE.txt
'''

####Python General Libraries
import os
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
############################

###third party################
import h5py
import numpy
from tqdm import tqdm
from scipy import interpolate
#############################

###SPARTAN_LIBS
from .                    import messages       as MTU
from .input_spartan_files import sp_input_files as PIF

class Retrieve_Lib_info:
    '''
    This class read the parameter space of the CSP base selected by the author
    '''

    def __init__(self):
        '''
        Class initialization
        '''
        #path to the directory where the libraries are stored
        self.indirlib = os.path.dirname(PIF().Base_LibP())

    def get_parameters(self, lib):

        '''
        Function that gets the parameters inside the base of the library provided
        in arguments. To do so we will go inside and look at it.

        Parameter
        ---------
        lib         str, name of the library base


        Return
        ------

        '''
        ##Get Param from name
        N = lib.split('_')
        Model = N[1]
        SFH = N[2]
        Res = N[3]
        IMF = N[4]

        lib_path = os.path.join(self.indirlib, lib)

        with h5py.File(lib_path, 'r') as LIB:
            #####extract secondary parameters names
            ex = self.keys(LIB)[0].split('_')
            Nparam = int((len(ex)-len(ex)%2)/2)
            i = 1
            Param_names = []
            while i < len(ex):
                Param_names.append(ex[i])
                i += 2
            #Create Nparam empty list
            list_empty = [[] for z in range(Nparam)]

            ##Fill the empty lists with parameter values
            for j in LIB:
                subgroup = j.split('_')
                if subgroup[0] == Model:
                    k = 0
                    while k <= len(ex)-2:
                        list_empty[int((k+2)/2.-1)].append(subgroup[k+2])
                        k += 2

            ##create a dictionnary with keywords==>set of values
            Param_final = {}
            for j in range(len(Param_names)):
                Param_final[Param_names[j]] = numpy.unique(list_empty[j])

            ##add ages
            Age = LIB['%s/Masses_SFR'%self.keys(LIB)[0]][0]
            Param_final['Age'] = Age

            Age_list = ''
            for k in Age:
                Age_list += '%1.2e\t'%k

        return Param_final

    def keys(self, filehdf5):
        '''
        Function that extracts all the group names inside the hdf5 file 'f'

        Parameters
        ----------
        filehdf5    hdf5 file open, file to look in

        Return
        ------
        list_name   list, of group name inside the file
        '''
        list_name = [key for key in filehdf5.keys()]

        return list_name


class Compil_provided_LIB:
    '''
    This class take all the parameters given by the user
    to the 'Provided' Library option and compile them in a hdf5 file
    '''

    def __init__(self):
        '''
        Class initialization, empty for the moment
        '''

    def Load_config(self, Lib_conf, project_conf):
        '''
        This function prepares the library compiler
        It takes the LIB and Project configuration to create the files and
        the parameter space.
        When we get to this point we do not need any further checking since
        the configuration was checked beforel.
        '''
        Name_LIB = os.path.join(project_conf['PDir'], project_conf['PName']+'_LIB.hdf5')

        lib_question = 'no'
        ##check if the file exists
        if os.path.isfile(Name_LIB):
            MTU.Info('Library already exists.....', 'Yes')
            ##If yes, ask the user if he wants to keep it or not
            lib_question = input('Do you want to recompile the library?\n'+\
                    '[Press enter to skip compilation, any other key+Enter to recompile]')
            if lib_question == '':
                return 'Written'
            else:
                os.remove(Name_LIB)

        if not os.path.isfile(Name_LIB):
            ##if not
            MTU.Info('Library does not exist or have been deleted...Creation...', 'No')
            #### We must create it
            ##1-Get the parameters from the user
            Base_SSP_name = Lib_conf['BaseSSP']
            Ages_USER = Lib_conf['Age']
            MET_USER = Lib_conf['MET']
            TAU_USER = Lib_conf['TAU']
            ##2-Get the parameters from the BaseSSP
            RLI = Retrieve_Lib_info()
            #Param_SSP = RLI.get_parameters('LIB_'+Base_SSP_name+'.hdf5')
            ###3- we select the good metallicity
            selectMET = self.select_good_MET(MET_USER,\
                    Base_SSP_name, RLI.indirlib)
            ###4- we regrid the ages od the SSP to the one of the user
            Ageinterpolation = self.regrid_AGE(selectMET, Ages_USER,\
                    Base_SSP_name, RLI.indirlib)
            ###5- we regrid the TAU values
            Final_SEDs = self.regrid_TAU(Ageinterpolation, TAU_USER)
            ###6- finally we write down the library
            status_write=self.Write_down_Lib(Final_SEDs, Name_LIB, Base_SSP_name, RLI.indirlib)

            return status_write


    def regrid_TAU(self, Ageinterp, TAU_USER):
        '''
        This function regride the provided models to the TAU requested by the user

        Parameter:
        ---------
        Ageinterp  list, of 3-element list with (subgroup_name,
                                  InterpMasses,InterpSpectra)
        TAU_USER    list, of TAU values from the user

        Return:
        ------
        '''

        ##first we check the TAU_values in the selected MET subgroup
        TAU = []
        for i in Ageinterp:
            subgroup = i[0].split('_')
            TAU.append(float(subgroup[4]))
        TAU = numpy.unique(TAU)

        ##then we check if some TAU given by the user are different from
        ##the provided list
        RECOMPUTE = 'NO'
        TAU_user = [float(i) for i in TAU_USER.split(';')]
        for i in TAU_user:
            if i not in TAU:
                RECOMPUTE = 'YES'

        if RECOMPUTE == 'NO':
            ##the tau from the user are already computed
            ##then we select only the tau from the user
            Age_FINAL = []
            for i in tqdm(Ageinterp, desc='Tau selection        '):
                subgroup = i[0].split('_')
                if float(subgroup[4]) in TAU_user:
                    Age_FINAL.append(i)

            return Age_FINAL

        else:
            print('RECOMPUTE')

    def regrid_AGE(self, selectMET, Ages_USER, Base_SSP_name, indirlib):
        '''
        This function regride the provided model to the Ages given by the USER
        It is done only for the selected metallicities

        Parameter
        --------
        selectMET       list of str, names of the subgroup of the SSPbase
                                 with the right metallicity
        Ages_USER       list of str, ages requested by the USER
        Ages_SSP        list of float, original Age grid of the SSP
        Base_SSP_name   str, name of the base SSP to use
        indirlib        str, path to the directory where the SSPbase are computed

        Return
        ------
        Interpolated_values list, of 3-element list with (subgroup_name,
                                  InterpMasses,InterpSpectra)
        '''
        ##1-open the lib
        lib_path = os.path.join(indirlib, 'LIB_'+Base_SSP_name+'.hdf5')
        with h5py.File(lib_path, 'r') as LIB:
            #2- We loop over each subgroup
            Interpolated_values = []
            for subgroup in tqdm(LIB, desc='Age interpolation    '):
                if subgroup != 'wavelength':
                    if subgroup in selectMET:
                        MASSES_SFR = numpy.array(LIB['%s/Masses_SFR'%subgroup])
                        Spectra = numpy.array(LIB['%s/spectra'%subgroup]).T
                        ##change age from user to float
                        Ages_user = [float(i) for i in Ages_USER.split(';')]
                        ##interpolate mass table
                        NEW_MASSES = interpolate.interp1d(MASSES_SFR[0], \
                                MASSES_SFR)(sorted(Ages_user))
                        ##interpolate spectra
                        NEW_SPECTRA = interpolate.interp1d(MASSES_SFR[0], \
                                Spectra.T)(sorted(Ages_user))
                        Interpolated_values.append([subgroup, NEW_MASSES, NEW_SPECTRA])

        return Interpolated_values

    def select_good_MET(self, MET_USER, Base_SSP_name, indirlib):
        '''
        This functions look in the SSP base hdf5 file and select only the metallicities
        That was selected by the USER.

        Parameter
        ---------
        MET_SSP     list, of metallicities contained in the SSP
        MET_USER    list, of metallicities selected by the user
        SSP_Base    str, name of the base SSP to be used
        indir_lib   str, path to the SSP_base directory

        Return
        ------
        Selected    list of str, names of the subgroups of the SSPbase
                                 with the right metallicity
        '''


        ##1-open the lib
        lib_path = os.path.join(indirlib, 'LIB_'+Base_SSP_name+'.hdf5')
        with h5py.File(lib_path, 'r') as LIB:
            #2-We look for the MET parameter in the names of the subgroups
            ex = Retrieve_Lib_info().keys(LIB)[0].split('_')
            Param_names = []
            i = 1
            while i < len(ex):
                Param_names.append(ex[i])
                i += 2

            for i in range(len(Param_names)):
                if Param_names[i] == 'MET':
                    MET_index = i+2

            #3-We select the header with the metallicity given by the user
            Selected = []
            for j in tqdm(LIB, desc='Metallicity Selection'):
                if j != 'wavelength':
                    subgroup = j.split('_')
                    if subgroup[MET_index] in MET_USER:
                        Selected.append(j)
        return Selected

    def Write_down_Lib(self, Final_SEDs, Name_LIB, Base_SSP_name, indirlib):
        '''
        This function organize and write down the library of SED to be used during the fits

        Parameter:
        ---------
        Final_SEDs  list, of 3-element list with (subgroup_name,
                                  InterpMasses,InterpSpectra)

        Name_LIB    str, path and name to the LIB to be written

        Result:
        -------
        '''

        ###initialization
        ##if finds the number of parameters and keep their names
        ex = Final_SEDs[0][0].split('_')
        Param_names = []
        i = 1
        while i < len(ex):
            Param_names.append(ex[i])
            i += 2

        TO_WRITE = []
        ###loop over FINAL_SED to organise the parameter and the library
        for j in tqdm(Final_SEDs, desc='Organization         '):
            subgroup = j[0].split('_')

            ###First we take the parameters from the subgroup name
            Param_FINAUX = []
            k = 0
            while k <= len(ex)-2:
                Param_FINAUX.append((subgroup[k+1], subgroup[k+2]))
                k += 2
            ##then we look at the masses and templates
            Masses = j[1].T
            Spectra = j[2].T

            ##we loop over the two arrays (they are of the same size)
            for i in range(len(Masses)):

                ###we create an empty column to be saved at in the big array of templates
                column_to_save = []
                ##we start to add subgroup parameters
                for k in Param_FINAUX:
                    column_to_save.append(float(k[1]))

                ##then the parameters from the mass file
                Param_masses = Masses[i]
                for k in Param_masses:
                    column_to_save.append(float(k))

                ##and finally the template itself
                Indiv_SED = Spectra[i]
                for k in Indiv_SED:
                    column_to_save.append(k)

                ##we aad the column to the general list of templates
                TO_WRITE.append(column_to_save)

        ##create the wavelentgh column
        ##must add fake entry (position of the parameters in the column)
        PARAM_SAVE = []
        WAVES = []
        for k in Param_FINAUX:
            WAVES.append(-99.9)
            PARAM_SAVE.append(k[0]) 

        Mass_Parameters = ['age', 'M*','SFR']
        
        Param_masses = Masses[i]
        for k, j in zip(Param_masses, Mass_Parameters):
            WAVES.append(-99.9)
            PARAM_SAVE.append(j)
        ###then we retrieve the wavelength from the LIB
        lib_path = os.path.join(indirlib, 'LIB_'+Base_SSP_name+'.hdf5')
        with h5py.File(lib_path, 'r') as LIB:
            waves = LIB['wavelength/wave']
            for i in waves[0]:
                WAVES.append(float(i))

        MTU.Info('Your Library contains %s templates'%len(TO_WRITE), 'No')
        MTU.Info('Trying to Write in the disk...', 'No')

        ##And write it down:
        try:
            with h5py.File(Name_LIB, "w") as f:
                f.create_dataset("Templates", data=TO_WRITE,\
                        compression='gzip', compression_opts=9)
                f.create_dataset("Wavelength", data=WAVES, \
                        compression='gzip', compression_opts=9)
                f.create_dataset("Parameter", data=numpy.array(PARAM_SAVE).astype('|S9'), \
                        compression='gzip', compression_opts=9)

            MTU.Info('Library created and saved', 'No')
            return 'Written'
        except:
            MTU.Error('Could not write down the Library', 'No')
            return 'Not Written'
