'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####      2016-2018
#####
#####   Read data file
#####      
#####
###########################
@License: GPL licence - see LICENCE.txt
'''

####Python Standard
import os
###################

###third party
import numpy
##############


class check_structure:
    """
    This class deals with the datafile reading
    """

    def check_s(self,Datafile,spec,phot,Nspec): 
        """
        This function checks the structure of the datafile

        Parameters
        ----------
        Datafile    String, containint path/to/file/and/file.dat

        Returns
        -------
        structure    int, 1 if the structure is ok; O otherwise
        message      message, if error, hint to the user to correct
        listmags     list of magnitude names in the catalogs
        """
        ###1-Extract header
        with open(Datafile, 'r') as f:
                fline = f.readline().rstrip()
        ###Check if the header starts by #
        if fline[0]!='#':
            return 0,'no # in header',[]

        ##Convert header in the list of columns names
        Header_list=fline[1:].split()

        ## Check if the length of the header list is equal
        ## to the number of column
        if len(Header_list)!=len(numpy.genfromtxt(Datafile).T):
            return 0,'NHeader \ndif Ncolumn',[]

        ##First case Photometry only
        if spec.lower()=='no':    
            arrayMags=Header_list[2:]
            mes,listmags=self.check_mag_list(arrayMags)
            if mes!='ok':
                return 0,mes,listmags

            else:
                return 1,mes,listmags
        
        ##Second case, Spectroscopy only         
        if spec.lower()=='yes' and phot.lower()=='no':
            ##Then we must check the format of spectra
            ##We define the position of the first spectrum,
            #according to the format to check the extension
            #[0:id, 1:redshift, 2:spec1, 3:err1, 4:spec2, 5:err2.....etc]
            N=2 
            if numpy.genfromtxt(Datafile, dtype='str').T[N][0][-4:]=='fits': 
                ##Column of the last spectrum [0: id, 1: redshift,2:spec1, 3:err1, 4:spec2, 5:err2.....etc]
                ###spectra are in fits format: 1 file for spec 1 file for error 
                Nmag=2+int(Nspec)
               

                ###select the right column in datafile for magnitudes
                arrayMags = []
                s = 0
                for kk in range(int(Nspec)):
                    arrayMags.append(Header_list[s+4])
                    arrayMags.append(Header_list[s+5])
                    s+=4

                #arrayMags=Header_list[Nmag:]
                mes,listmags=self.check_mag_list(arrayMags)
                if mes!='ok':
                    return 0,mes,listmags

                else:
                    return 1,mes,listmags

            
            elif numpy.genfromtxt(Datafile, dtype='str').T[N][0][-4:]=='spec':
                ##Column of the last spectrum [0: id, 1: redshift,2:spec1, 3:spec2, 4:spec3...]
                ###spectra are in ascii format: 1 file with 3 columns [l,f,err]

                ###number of magnitude column --> 2 (meas and err) per spectrum
                Nmag=2+int(Nspec)

                ###select the right column in datafile for magnitudes
                arrayMags = []
                s = 0
                for kk in range(int(Nspec)):
                    arrayMags.append(Header_list[s+3])
                    arrayMags.append(Header_list[s+4])
                    s+=3

                mes,listmags=self.check_mag_list(arrayMags)
                if mes!='ok':
                    return 0,mes,listmags

                else:
                    return 1,mes,listmags


            return 1,'ok',[]
            
        ## Thirs case, Photometry and spectroscopy
        if spec.lower()=='yes' and phot.lower()=='yes':
            ##Then we must check the format of spectra
            ##We define the position of the first spectrum, according to the format to check the extension
            #[0: id, 1: redshift,2:spec1, 3:err1, 4:spec2, 5:err2.....etc]
            N=2 
            if numpy.genfromtxt(Datafile, dtype='str').T[N][0][-4:]=='fits': 
                ##Column of the last spectrum [0: id, 1: redshift,2:spec1, 3:err1, 4:spec2, 5:err2.....etc]
                ###spectra are in fits format: 1 file for spec 1 file for error 
                Nmag=1+2*int(Nspec)+1
                arrayMags=Header_list[Nmag:]
                mes,listmags=self.check_mag_list(arrayMags)
                if mes!='ok':
                    return 0,mes,listmags

                else:
                    return 1,mes,listmags


            elif numpy.genfromtxt(Datafile, dtype='str').T[N][0][-4:]=='spec':
                ##Column of the last spectrum [0: id, 1: redshift,2:spec1, 3:spec2, 4:spec3...]
                ###spectra are in ascii format: 1 file with 3 columns [l,f,err]

                ##extract spectroscopy magnitude
                arrayMags = []
                n = 1
                for i in range(int(Nspec)):
                    j = i+1
                    arrayMags.append(Header_list[2+j*n])
                    arrayMags.append(Header_list[3+j*n])
                    n += 1

                ### and from the mag file
                Nmag=2+3*int(Nspec)
                arrayMags+=Header_list[Nmag:]
                mes,listmags=self.check_mag_list(arrayMags)
                if mes!='ok':
                    return 0,mes,listmags

                else:
                    return 1,mes,listmags


            return 1,'ok',[]
         


    def check_mag_list(self,ArrayMags):
        
        ##We first check if the number of column is even
        ##(For each magnitude we need the measurement and an error)
        if len(ArrayMags)%2!=0:
            return 'Ncol must be even',[]
       
        ##Then we check if for each mag column we have an associated 
        ## error column 
        MAGS=[]
        for i in range(len(ArrayMags)):
            if i%2==0:
                Magname=str(ArrayMags[i])  ###Magnitude column name
                Magnamefromerr=str(ArrayMags[i+1][:len(Magname)])  ##Magnitude name from err column
                err_suffix=str(ArrayMags[i+1][-4:])#Check if it is the error column

                if Magname==Magnamefromerr and err_suffix=='_err':
                   MAGS.append(Magname)
                else:
                    return 'Bad column names',[]

        ##Finally we check if the number of mags is equal to the
        ##number of magnitude columns/2 
        if len(MAGS)==len(ArrayMags)/2:
           return 'ok',MAGS
        

class extract_mag_names:
    """
    This class extract the array of magnitude in the header of the datafile
    """
    def __init__(self):
        """
        Class Constructor, empty for the moment
        """
        pass

    def extract(self,Datafile,spec,phot,Nspec):
        
        #First we need to check the structure
        s,mes,listmags=check_structure().check_s(Datafile,spec,phot,Nspec)  
        
        if s==0:
            return [],mes
        
        if s==1:
            return listmags,mes
