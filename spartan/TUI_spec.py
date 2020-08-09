'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
#####   File of the spectro 
#####       page TUI
#####
###########################
@License: GPL v3 licence - see LICENCE.txt
'''
#####Third Party###
import npyscreen
###################

class Spec_win:
    """
        This class manages the spectroscopic section of the TUI: the spectroscopy configuration
        
        Attributes:
            self.SDir           Spectra Directory
            self.Funit          Flux Unit
            self.Wunit          Wavelength Unit
            self.Skip           Skip edges choice
            self.SSkip          if previous =Yes, siwe to skip
            self.UseBR          Use bad Regions choice
            self.BR             If previous =Yes, list of Bad regions 
            self.S              Npyscreen Form
    
    """

    def __init__(self,Log,x,y,SPEC):

        """
        Class constructor creating the form and populating it with widgets
        Parameters:
        ----------
        SPEC:  An Dictionnaey containing the information of each widget 
               It can be empty or coming from an already defined Project
               Format={Spectra directory, Use Full,binning, specz,\
               Funits, Wunits,Skip, Sizeskip,Use BR,Bad Regions}
               Types={str,int,str,int,str,str,int,str,int,str}
        Log:   SPARTAN LOGO to be drawn at the top of the form
                                                                                                                                 
        x,y:   size of the front page of the TUI. The nez page descibed here 
               is drawn on the same size.

        Returns:
        -------
        """

        ##Initialize form and write logo
        self.S  = npyscreen.Form(name = "SPARTAN Spectroscopic configuration",color='STANDOUT')

        ###Write the Logo
        for i in Log:
            self.S.add(npyscreen.FixedText,value=i,relx=int((x-len(i))/2),editable=False\
                    , color='CURSOR')  

        ### Make the 3 boxes
        n=9  ### Terminal row where we start to draw the boxes
        self.S.add(npyscreen.BoxBasic,name='Spectroscopy', rely=n\
                ,max_width=int(x/2)-1, max_height = int(y/2.5), editable=False, color='DANGER')
        
        self.S.add(npyscreen.BoxBasic,name='Bad Regions'\
                ,relx=int(x/2)+1,rely=n, max_height = int(y/2.5),editable=False, color='DANGER')
        self.S.add(npyscreen.BoxBasic,name='FIT'\
                ,rely=n+int(y/2.5),editable=False, color='DANGER')


        #### Create the option lists [for F units and W units] 
        Options = npyscreen.OptionList() 
        options = Options.options
        options.append(npyscreen.OptionSingleChoice('Units (Flux)', \
                choices=specunits().Funitchoice))
        options.append(npyscreen.OptionSingleChoice('Units (Wavelength)', \
                choices=specunits().Wunitchoice))
        

        #### Create the widgets 
        n=10  ###Terminal row where se start to draw widgets
        SDir=self.S.add(npyscreen.TitleFilenameCombo, name = "Spectra Directory [tab]:",\
                value=SPEC['SDir'],relx=5,rely=n,max_width=int(x/2.5), labelColor='CAUTION')
       
        Res=self.S.add(npyscreen.TitleText,name='Resolution(Ang):',\
                relx=5,rely=n+int((y-n)/6),max_height=3,max_width=int(x/2-10), \
                value=SPEC['Res'],labelColor='CAUTION')        

        ListUNITS=self.S.add(npyscreen.OptionListDisplay, \
                name="Option List",values = options,relx=5,rely=n+2*int((y-n)/6),scroll_exit=True,\
                max_width=int(x/2.5),max_height=int(2), color='CAUTION')  


        if type(SPEC['Funit'])==list:
            options[0].set(SPEC['Funit'])
        elif type(SPEC['Funit'])==str:
            options[0].set([SPEC['Funit']])


        if type(SPEC['Wunit'])==list:
            options[1].set(SPEC['Wunit'])
        elif type(SPEC['Wunit'])==str:
            options[1].set([SPEC['Wunit']])

        ###bad regions box

        if SPEC['Skip'].lower()=='yes':
            SKIP=1
        elif SPEC['Skip'].lower()=='no':
            SKIP=0
        else:
            SKIP=''


        Skip=self.S.add(npyscreen.TitleSelectOne,  name="Skip edges",\
                values = ["NO","YES"],value=SKIP, scroll_exit=True, labelColor='CAUTION',\
                relx=int(x/2)+5,rely=n,max_height=int(y/15),max_width=int(x/3)) 
        
        SSkip=self.S.add(npyscreen.TitleText, name = "Size to skip (AA,obs-f) :", labelColor='CAUTION',\
                value=SPEC['SSkip'],rely=n+int((y-n)/8),relx=int(x/2)+5,max_width=int(x/3)) 

        if SPEC['UseBR'].lower()=='yes':
            USEBR=1
        elif SPEC['UseBR'].lower()=='no':
            USEBR=0
        else:
            USEBR=''

        UseBR=self.S.add(npyscreen.TitleSelectOne,  name="Bad regions",\
                values = ["NO","YES"],value=USEBR, scroll_exit=True, labelColor='CAUTION',\
                relx=int(x/2)+5,rely=n+3*int((y-n)/10),max_height=int(y/15),max_width=int(x/3)) 
        
        #self.S.nextrely += 1
        BR = self.S.add(npyscreen.TitleText, name='If Yes, list (rest-f, AA).',\
                value=SPEC['BR'],relx=int(x/2)+5,rely=n+4*int((y-n)/10),max_width=int(x/3),color='CAUTION') 
        

        ###normalisation 
        if SPEC['Norm'].lower()=='mags':
            Norm=0
        elif SPEC['Norm'].lower()=='region':
            Norm=1
        else:
            Norm=0
        Norm=self.S.add(npyscreen.TitleSelectOne,  name="Nor Dat/Mod",\
                values = ["Magnitude","Regions"],value=Norm, scroll_exit=True, labelColor='CAUTION',\
                relx=5,rely=n+4*int((y-n)/6),max_height=int(y/15),max_width=int(x/3)) 

        NormReg = self.S.add(npyscreen.TitleText, name='If Region, give l1 & l2 (rest-f ,AA :l1-l2).',\
                  value=SPEC['Norm_reg'],relx=5,rely=n+5*int((y-n)/6),max_width=int(x/3),color='CAUTION') 

        ######Multi_spec calibration
        if SPEC['Calib'].lower()=='yes':
            fitcalib=1
        elif SPEC['Calib'].lower()=='no':
            fitcalib=0
        else:
            fitcalib=1
        Calib=self.S.add(npyscreen.TitleSelectOne,  name="Fit multi-spec calib",\
                values = ["Yes","No"],value=fitcalib, scroll_exit=True, labelColor='CAUTION',\
                relx=int(x/2)+5,rely=n+4*int((y-n)/6),max_height=int(y/6), max_width = int(x/3)) 
        

        ###To let the user interact with the screen        
        self.S.edit()

        ###Define the attributes of the class

        self.SDir=SDir.value
        self.Res = Res.value
        self.Funit=options[0].get()
        self.Wunit=options[1].get()
        self.SSkip=SSkip.value
        self.BR=BR.value
        self.Norm_reg=NormReg.value

        if Skip.value[0]==1:
            self.Skip='Yes'  
        elif Skip.value[0]=='':
            self.Skip=''
        elif Skip.value[0]==0:
            self.Skip='No'

        if UseBR.value[0]==1:
            self.UseBR='Yes'  
        elif UseBR.value[0]=='':
            self.UseBR=''
        elif UseBR.value[0]==0:
            self.UseBR='No'
        
        if Calib.value[0]==1:
            self.Calib = 'No'  
        elif Calib.value[0]=='':
            self.Calib = 'No'
        elif Calib.value[0]==0:
            self.Calib = 'Yes'

        if Norm.value[0]==1:
            self.Norm = 'region'  
        elif Norm.value[0]=='':
            self.Norm = 'mags'
        elif Norm.value[0]==0:
            self.Norm='mags'


class specunits:
    """
    class listing the spectrscopic unit proposed to the user
    
    Attributes:
    ----------
    self.Funitchoice    List of possible flux units
    self.Wunitchoice    List of possible wavelength units
    
    """

    def __init__(self):
        """
        Class constructor, defining the attributes listed above
        """
        self.Funitchoice=['erg/s/cm2/A']
        self.Wunitchoice=['Ang']
