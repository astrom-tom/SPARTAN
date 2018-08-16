'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
#####   File of the provided library 
#####       page TUI
#####
###########################
@License: CeCILL-v2 licence - see LICENCE.txt
'''
####python standard#####
import os
########################

###python third party###
import npyscreen
import numpy
########################

####Local imports
from .Lib_provided        import Retrieve_Lib_info as Retr
from .input_spartan_files import sp_input_files as PIF

###define the external files to be used
class LibProvided_win:
    """
    This class imports the externally created library section of the TUI: the Import library configuration
                            
    Attributes:
        self.ImportedLib      imported Library
    """
    

    def __init__(self,Log,x,y,LIB_P):

        """
        Class constructor creating the form and populating it with widgets
        Parameters:
        ----------
        LIB_I:  An array containing the information of each widget 
                It can be empty or coming from an already defined Project
                Format=[path+lib]
                Types=[str]
                                                                                                        
        Log:    SPARTAN LOGO to be drawn at the top of the form
                                                                                                                        
        x,y:    size of the front page of the TUI. The nez page descibed here 
                is drawn on the same size.

        Returns:
        -------
        """
        ##define external file to be used
        LIB_list_files=PIF().Base_LibP()
        EXT_list_files=PIF().Dust()

        ##size of the terminal
        self.x=x
        self.y=y

        ##Initialize form and write logo
        self.LibP  = npyscreen.Form(name = "SPARTAN Create library from SPARTAN templates",\
                color='STANDOUT')
         
        #### Make the template base box
        n=1
        self.LibP.add(npyscreen.BoxBasic,name='Base [Model/SFH/Met/IMF/AGEs]',\
                rely=n,max_width=int(x/2)-1,editable=False, color='DANGER')
        
        ##try to load the lib file
        try:
            Lib_list=numpy.genfromtxt(LIB_list_files,dtype='str').T
            Libdir=os.path.dirname(LIB_list_files)

            list_buttons=[]
            list_buttons.append('none')
            for i in Lib_list:
                if os.path.isfile(os.path.join(Libdir,i))==True:
                    list_buttons.append(i[4:-5])
            ##select the one in the conf file
            if LIB_P['BaseSSP'] not in list_buttons:
                N=0
                
            else:
                N=0
                for i in list_buttons:
                    if i==LIB_P['BaseSSP']:  
                        break
                    N+=1 
        except:
            list_buttons=['Lib file not found']


        Base=self.LibP.add(npyscreen.SelectOne,rely=n+1,relx=3,\
                values = list_buttons, value=N,scroll_exit=True, name=' ',\
                max_width=int(x/2)-3,max_height=y-5,labelColor='CAUTION')

        
        n=1 
        ###extinction box
        self.LibP.add(npyscreen.BoxBasic,name='Extinction [Dust & IGM]',\
                    relx=int(x/2)+1,rely=n,max_height=int(y/2.5),editable=False,
                    color='DANGER')
        
        ###to populate with widget
        ## Try to load the extinctin list
        try:
            Ext_list=numpy.genfromtxt(EXT_list_files,dtype='str').T
            Extdir=os.path.dirname(EXT_list_files)
            ##populate the list of name from the list in the ext file
            list_ext=[]  
            list_ext.append("none")
            for i in Ext_list:
                if os.path.isfile(os.path.join(Extdir,i))==True:
                    list_ext.append(i[:-4].lower())
            ##select the one in the conf file
            if LIB_P['DustUse'] not in list_ext:
                N=0
            else:
                N=0
                for i in list_ext:
                    if i==LIB_P['DustUse']:  
                        break
                    N+=1
        
        except:
            list_ext=['Ext file','not found']


        #####################DUST
        DustUse=self.LibP.add(npyscreen.TitleSelectOne,  name="Dust",values = list_ext,value=N, \
                scroll_exit=True,relx=int(x/2)+2,rely=n+1,max_height=4,\
                max_width=int(x/2.5),labelColor='CAUTION')
     
        EBVList=self.LibP.add(npyscreen.TitleText,name='E(B-V) [XX;YY...]:',\
                value=LIB_P['EBVList'],relx=int(x/2)+2,rely=n+6,\
                max_height=4,max_width=int(x/2.5), labelColor='CAUTION') 
        
        #################IGM
        IGM_list=["none", "mean_meiksin", "mean_madau", "free_meiksin", "free_madau"]
        if LIB_P['IGMtype'].lower() not in IGM_list:
            N=0
        
        else:
            N=0
            for i in IGM_list:
                if i==LIB_P['IGMtype'].lower():
                    break    
                N+=1

        IGMtype=self.LibP.add(npyscreen.TitleSelectOne,  name="IGM",values = IGM_list,value=N, \
                scroll_exit=True, relx=int(x/2)+2,rely=n+8,max_height=3,max_width=int(x/2.5),\
                labelColor='CAUTION')

        ###Emission line box
        n=int(y/2.5)
        self.LibP.add(npyscreen.BoxBasic,name='Emission lines',\
                    relx=int(x/2)+1,rely=n+1,editable=False,\
                    color='DANGER')
       
        list_EMline=["Yes","No"]
        if LIB_P['EMline'].lower() == 'yes':
            USE = 0
        elif LIB_P['EMline'].lower() == 'no':
            USE = 1
        else:
            USE = 1

        EMLine=self.LibP.add(npyscreen.TitleSelectOne,  name="Em.Lines",values =list_EMline,value=USE, \
                scroll_exit=True, relx=int(x/2)+2,rely=n+3,max_height=3,max_width=int(x/2.5),\
                labelColor='CAUTION')

        EMline_skipped=self.LibP.add(npyscreen.TitleText,name='Skipped Em line [line1;line2...]:',\
                value=LIB_P['Emline_skipped'],relx=int(x/2)+2,rely=n+8,\
                max_height=4,max_width=int(x/2.5), labelColor='CAUTION') 
        
        ###To let the user interact with the screen 
        self.LibP.edit()

        ###Define the attributes of the class
        if EMLine.value!=[]:
            self.EMline=list_EMline[EMLine.value[0]]
        else:
            self.EMline='NOTGIVEN'
       
        self.Emline_skipped = EMline_skipped.value

        if DustUse.value!=[]:
            self.DustUse=list_ext[DustUse.value[0]] 
        else:
            self.DustUse='NOTGIVEN'

        self.EBVList=EBVList.value 
        

        if IGMtype.value!=[]:
            self.IGMtype=IGM_list[IGMtype.value[0]]
        else:
            self.IGMtype='NOTGIVEN'

        self.BaseSSP=Base.value
 
        if self.BaseSSP!=[] and list_buttons[Base.value[0]]!='none':
            
            Basename='LIB_'+list_buttons[Base.value[0]]+'.hdf5'
            BaseParam=Libbase(self.x,self.y,Basename,LIB_P)
            self.Param=BaseParam.__dict__
            self.Param.pop('x',None)
            self.Param.pop('y',None)
            self.Param.pop('L1',None)
            self.BaseSSP=list_buttons[Base.value[0]]

        else:
            self.BaseSSP='None'
            self.Param={}



    def buttontoBase(self):
        P=Libbase(self.x,self.y,base)



class Libbase:

    def __init__(self,x,y,Tbase,LIB_P):
        '''
        This function creates the frame for the parameters of the base selected
        by the user.

        Parameter
        ----------
        base,   str, Name of the template based selected by the user.                                                                                                        
                                                                                                                        
        x,y:    size of the front page of the TUI. The nez page descibed here 
                is drawn on the same size.

        Returns:
        -------
        '''
        self.x=x
        self.y=y

        ###Retrieve the parameters from the base file
        Param_Base=Retr().get_parameters(Tbase)


        ##Initialize form 
        self.L1  = npyscreen.Form(name = "SPARTAN LIB, Select Age, metallicity and SFH timescale",color='CURSOR') 
        n=1
        
        ###Make the boxes and populate with widget
        self.L1.add(npyscreen.BoxBasic,name='Information',rely=n,max_height=int(y/4)-1,editable=False)
        val='This screen allows you to select the parameter of the base of your \nlibrary. '+\
                'You can remove/add values, but please do not add values \n'+'outside the ranges.'
        self.L1.add(npyscreen.MultiLineEdit,value=val,relx=3,rely=n+1,\
                    max_width=int(x-10),max_height=int(y/4)-3,editable=False)
         
        MAXH=int(y/4)
        ##make the widget and populate them
        WIDGETS=[]
        for i in Param_Base.keys():
            self.L1.add(npyscreen.BoxBasic,name=i,max_height=int(y/(len(Param_Base.keys())+1)),rely=MAXH,editable=False) 
            v,colortext=check_param_base().check_input_vs_output(LIB_P,Param_Base[i],i,x)    
            W=self.L1.add(npyscreen.MultiLineEdit,value=v,relx=3,rely=MAXH+1,\
                    max_width=int(x-10),max_height=int(y/(len(Param_Base.keys())+1))-2,color=colortext)

            WIDGETS.append([W,i])
            MAXH+=int(y/(1+len(Param_Base.keys())))

        self.L1.edit()

        ###define the attributes 
        Parameter={} 
        for i in WIDGETS:
            Parameter[i[1]]=i[0].value

        self.Parameter=Parameter


class check_param_base:

    def Make_list(self,array,Param,x):
        '''
        function that display the list

        Parameter
        ---------
        array   list, of value for a given parameter
        Param   str, Param name
        x       int, x-size of the terminal

        Return
        ------
        string_to_display   str, value to insert in the widget
        '''

        N=0
        std=''
        for i in array:
            if Param!='Age':
                std+='%s;'%i
            else:
                std+='%1.2e;'%i

        X=x-10
        string_cut=[ std[i:i+X] for i in range(0, len(std),X ) ]

        string_to_display=''
        for i in string_cut:
            string_to_display=string_to_display+i+'\n'

        return string_to_display

    def check_input_vs_output(self,User_input,List_from_base,paramname,x):
        """
        Here we check if the parameters base parameters givern by the user
        are included in the library

        Parameters:
        -----------
        User_input      dict with user input parameter
        List_from_base  list of allowed parameter 
        paramname       name of the parameter
        x               ???

        Return:
        -------
        final list      final list of parameters
        color           color of the parameter to be displayer. Red-->not good
                        green --> good
        """
        for i in User_input.keys():
            if i==paramname:
                if len(User_input[i])!=0:
                    listvalue=User_input[i].split(';')
                    ####AGE 
                    if paramname=='Age': 
                        listvalue=[float(i) for i in listvalue]
                        minAge=min(List_from_base)
                        maxAge=max(List_from_base)
                        if min(listvalue)<minAge or max(listvalue)>maxAge:
                            color='LABEL'
                        else:
                            color='CURSOR'
                    
                    ##check TAU
                    elif paramname=='TAU':
                        values=[float(i) for i in listvalue]
                        BASE=[float(i) for i in List_from_base]
                        minTAU=min(BASE)
                        maxTAU=max(BASE)
                        if min(values)<minTAU or max(values)>maxTAU:
                            color='LABEL'
                        else:
                             color='CURSOR'
                    
                    ###check metallicity
                    elif paramname=='MET':    
                        OK='yes'
                        for k in listvalue:
                            ## if one value of the metallicity is not in the base list
                            ## the parameters are not ok
                            if k not in List_from_base:
                                OK='no'

                        ##if everythiong is ok we put the green color
                        if OK=='yes':
                            color='CURSOR'
                        else:
                            color='LABEL'

                else:
                    listvalue=List_from_base
                    color='LABEL'
        Final_list=self.Make_list(listvalue,paramname,x)
        return Final_list,color

