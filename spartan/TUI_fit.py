'''
############################
#####
##### The Spartan Project
#####      R. THOMAS
#####        2016
#####
#####   File of the fit
#####       page TUI
#####
###########################
@License: GPL - see LICENCE.txt
'''
###Third Party###
import npyscreen
#################

class Fit_win:
    """
    This class manages the Fitting section of the TUI: fitting configuration

    Attributes:
        self.Algo       ALGOrithm choice
        self.OverFit    Allow Overfit
        self.PDFV       PDF values
        self.BFV        BFV values
        self.KeepPDF    Keepfull PDF
        self.Combined   how to combined phot and spec

    """
    def __init__(self, Log, x, y, FIT):

        """
        Class constructor creating the form and populating it with widgets
        Parameters:
        ----------
        FIT:    An array containing the information of each widget
                It can be empty or coming from an already defined Project
                Format={Algo,Overfit, Decision Tree, colorsDR,PDFvalues,\
                        BestFitValues,KeepPDF,WeightsMethod,WeightsPerso}
                Types={int,int,int,str,int,int,int,int,str}

        Log:    SPARTAN LOGO to be drawn at the top of the form

        x,y:    size of the front page of the TUI. The new page descibed here
                is drawn on the same size.

        Returns:
        -------
        """

        ##Initialize form and write logo
        self.Fi = npyscreen.Form(name="SPARTAN Fitting information", color='STANDOUT')
        for i in Log:
            self.Fi.add(npyscreen.FixedText, value=i, relx=int((x-len(i))/2), editable=False)


        #### Creates the boxes
        n = 9 ###terminal row where we draw the boxes
        self.Fi.add(npyscreen.BoxBasic, name='Fit', rely=n, max_width=int(x/2)-1, \
                editable=False, color='DANGER')
        self.Fi.add(npyscreen.BoxBasic, name='Output', relx=int(x/2)+1, rely=n, \
             editable=False, color='DANGER')

        #### Populate the frame with widgets

        n = 10
        if FIT['Algo'].lower() == 'mcmc(soon)':
            ALGO = 0
        elif FIT['Algo'].lower() == 'chi2':
            ALGO = 0
        elif FIT['Algo'].lower() == '':
            ALGO = 0

        Algo = self.Fi.add(npyscreen.TitleSelectOne, value=ALGO, name="Algorithm",\
                 relx=6, rely=n, values=["CHI2", "MCMC(soon)"], scroll_exit=True,\
                 max_width=int(x/2.5), max_height=4, labelColor='CAUTION')

        if FIT['Combined'].lower() == 'full':
            COMB = 0
        elif FIT['Combined'].lower() == 'complementary':
            COMB = 1
        elif FIT['Combined'].lower() == '':
            COMB = 1

           
        Comb = self.Fi.add(npyscreen.TitleSelectOne, value=COMB, name="Combined",\
                 relx=6, rely=n+int((y-n)/3), values=["Full", "Complementary"], scroll_exit=True,\
                 max_width=int(x/2.5), max_height=4, labelColor='CAUTION')

 
        if FIT['OverFit'].lower() == 'yes':
            OVER = 1
        elif FIT['OverFit'].lower() == 'no':
            OVER = 0
        else:
            OVER = 0

        OverF = self.Fi.add(npyscreen.TitleSelectOne, value=OVER, name="Allow overfit",\
                 values=["NO", "YES"], scroll_exit=True, relx=6, rely=n+2*int((y-n)/3),\
                 max_height=3, max_width=int(x/2.5), labelColor='CAUTION')

        ##OUTPUT
        if FIT['PDFV'].lower() == 'yes':
            PDF = 1
        elif FIT['PDFV'].lower() == 'no':
            PDF = 0
        else:
            PDF = 1

        PDFV = self.Fi.add(npyscreen.TitleSelectOne, name="PDF Values", value=PDF,\
                 values=["NO", "YES"], scroll_exit=True, labelColor='CAUTION',\
                 relx=int(x/2)+5, rely=n, max_height=2, max_width=int(x/3))

        if FIT['BFV'].lower() == 'yes':
            BEST = 1
        elif FIT['BFV'].lower() == 'no':
            BEST = 0
        else:
            BEST = 1

        BFV = self.Fi.add(npyscreen.TitleSelectOne, name="Best Fit ", value=BEST,\
                 values=["NO", "YES"], scroll_exit=True, labelColor='CAUTION',\
                 relx=int(x/2)+5, rely=n+int((y-n)/3), max_height=2, max_width=int(x/3))

        if FIT['KeepPDF'].lower() == 'yes':
            Keep = 1
        elif FIT['KeepPDF'].lower() == 'no':
            Keep = 0
        else:
            Keep = 0

        KeepPDF = self.Fi.add(npyscreen.TitleSelectOne, name="Keep Full PDF", value=Keep,\
                values=["NO", "YES"], scroll_exit=True, labelColor='CAUTION',\
                relx=int(x/2)+5, rely=n+2*int((y-n)/3), max_height=2, max_width=int(x/3))

        ###To let the user interact with the screen
        self.Fi.edit()

        ###Define the attributes of the class

        if Algo.value[0] == 0:
            self.Algo = 'CHI2'
        elif Algo.value[0] == '':
            self.Algo = ''
        elif Algo.value[0] == 1:
            self.Algo = 'MCMC(soon)'


        if OverF.value[0] == 1:
            self.OverFit = 'Yes'
        elif OverF.value[0] == 0:
            self.OverFit = 'No'
        else:
            self.OverFit = ''

        if Comb.value[0] == 1:
            self.Combined = 'complementary'
        elif Comb.value[0] == 0:
            self.Combined = 'full'
        else:
            self.Combined = ''




        if PDFV.value[0] == 1:
            self.PDFV = 'Yes'
        elif PDFV.value[0] == 0:
            self.PDFV = 'No'
        else:
            self.PDFV = ''

        if BFV.value[0] == 1:
            self.BFV = 'Yes'
        elif BFV.value[0] == 0:
            self.BFV = 'No'
        else:
            self.BFV = ''

        if KeepPDF.value[0] == 1:
            self.KeepPDF = 'Yes'
        elif KeepPDF.value[0] == 0:
            self.KeepPDF = 'No'
        else:
            self.KeepPDF = ''
