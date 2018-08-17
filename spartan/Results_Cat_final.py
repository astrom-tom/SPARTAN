'''
The SPARTAN Project
-------------------
This module creates, and save
the final catalog of parameters

@author: R. THOMAS
@year: 2016
@place: UV/LAM/UCBJ
@License: GPL v3.0 - see LICENCE.txt
'''
##Python Standard
import os
#################

###Third party#
import numpy
import h5py
###############



def final(CONF, Res):
    '''
    function that creates the final catalog of parameters
    Parameter:
    ----------
    CONF        dict, configuration from the user
    Res         str,  Result file (hdf5)

    Return:
    -------
    None,       written on disk
    '''

    ###1 - Create name of catalog and open it in write mode
    catname = os.path.join(CONF.CONF['PDir'], CONF.CONF['PName']+'.catalog') 
    cat = open(catname, 'w')

    ###2 - Open result file
    R = h5py.File(Res)

    ####look at all the groups for a given object
    obj1 = R[list(R.keys())[0]]
    if 'Parameters_BF' in list(obj1.keys()):
        all_param_BF = []
    if 'Parameters_PDF' in list(obj1.keys()):
        all_param_PDF = []
    if 'Mag_abs' in list(obj1.keys()):
        all_magabs = []
    if 'Template' in list(obj1.keys()):
        all_Template = []
    if 'Observable' in list(obj1.keys()):
        all_Observable = []
    #print(list(obj1.keys()))
    
    #for each object we look at the parameters
    #in each group
    for i in R:
        obj = R[i]
        Fitted = str(numpy.array(obj['General/Fitted']))[2:-1].lower() 
        if Fitted == 'fitted':
            if 'Parameters_BF' in list(obj1.keys()):
                for j in obj['Parameters_BF']:
                    all_param_BF.append('BF_' + j)
            if 'Parameters_PDF' in list(obj1.keys()):
                for j in obj['Parameters_PDF']:
                    all_param_PDF.append('PDF_' + j)
            if 'Mag_abs' in list(obj1.keys()):
                for j in obj['Mag_abs']:
                    all_magabs.append(j)
            if 'Template' in list(obj1.keys()):
                if 'Bestchi2' in obj['Template']:
                    all_Template.append('Bestchi2')
            if 'Observable' in list(obj1.keys()):
                if 'Redshift' in obj['Observable']:
                    all_Observable.append('Redshift')
                if CONF.CONF['UseSpec'] == 'yes' and CONF.CONF['UsePhot'] == 'yes':
                    if 'Npoints_spec' in obj['Observable']:
                        all_Observable.append('Npoints_spec')
                    if 'Npoints_mags' in obj['Observable']:
                        all_Observable.append('Npoints_mags')
                else:
                    if 'Npoints' in obj['Observable']:
                        all_Observable.append('Npoints')

    ####then we take all the unique parameters in each list
    if 'Parameters_BF' in list(obj1.keys()):
        unique_PDF = numpy.unique(all_param_PDF)
    if 'Parameters_PDF' in list(obj1.keys()):
        unique_BF = numpy.unique(all_param_BF)
    if 'Mag_abs' in list(obj1.keys()):
        unique_mag = numpy.unique(all_magabs)
    if 'Template' in list(obj1.keys()):
        unique_Temp = numpy.unique(all_Template)
    if 'Observable' in list(obj1.keys()):
        unique_Obs = numpy.unique(all_Observable)

    #print(unique_PDF)
    #print(unique_BF)
    #print(unique_mag)
    #print(unique_Temp)
    #print(unique_Obs)

    ###Creates the header: 
    if CONF.CONF['UseSpec'].lower() == 'yes' and CONF.CONF['UsePhot'].lower() == 'yes':
        header = '#Ident\tredshift\tNpoint_spec\tNpoint_mags\tBestchi2\t'
        headers = ['ide', 'z', 'Npoint_spec', 'Npoint_mags', 'Chi2min']
    else:
        header = '#Ident\tredshift\tNpoints\tBestchi2\t'
        headers = ['ide', 'z', 'Npoints', 'Chi2min']

    if 'Parameters_PDF' in list(obj1.keys()):
        for i in unique_PDF:
            header += '%s\tm1s_%s\tp1s_%s\t'%(i, i, i)
            headers.append(i)
            headers.append(i)
            headers.append(i)

    if 'Parameters_BF' in list(obj1.keys()):
        for i in unique_BF:
            header += '%s\t'%i
            headers.append(i)

    if 'Mag_abs' in list(obj1.keys()):
        for i in unique_mag:
            header += '%s_Abs\t'%i
            headers.append(i)

    ###and write it down
    header += '\n'
    cat.write(header)

    ###and we create the catalog
    for i in R:
        obj=R[i]
        #print(list(obj.keys()))
        h = []
        Fitted = str(numpy.array(obj['General/Fitted']))[2:-1].lower()
        if Fitted == 'fitted':
            ####in Observable we take Npoints and Redshift
            Redshift = float(numpy.array(obj['Observable/Redshift']))

            if CONF.CONF['UseSpec'].lower() == 'yes' and CONF.CONF['UsePhot'].lower() == 'yes':
                Npoints_spec = int(float(numpy.array(obj['Observable/Npoints_spec'])))
                Npoints_mags = int(float(numpy.array(obj['Observable/Npoints_mags'])))
                line = '%s\t%s\t%s\t%s\t'%(i, Redshift, Npoints_spec, Npoints_mags)
            else:
                Npoints = int(float(numpy.array(obj['Observable/Npoints'])))
                line = '%s\t%s\t%s\t'%(i, Redshift, Npoints)

            ###in Template we take the best chi2
            Bestchi2 =  round(float(numpy.array(obj['Template/Bestchi2'])), 2)
            line += '%s\t'%Bestchi2 
            #h.append('bestchi2')

            ####
            if len(list(obj.keys())) < 3 :
                line = ''
                for i in headers:
                    line +=  '-99\t'

            else:
                if 'Parameters_PDF' in list(obj.keys()):
                    listParam_PDF = list(obj['Parameters_PDF'].keys())
                    for j in unique_PDF:
                        if j[4:] in listParam_PDF:
                            P = numpy.array(obj['Parameters_PDF/%s'%(j[4:])])
                            if P.size == 3:
                                if numpy.isnan(P[0]):
                                    line +=  '-99\t-99\t-99\t'
                                else:
                                    line += '%s\t%s\t%s\t'%(round(P[0],3), round(P[1],3), round(P[2],3))
                            elif P.size == 1:
                                line += '%s\t%s\t%s\t'%(round(P,3), -99.9, -99.9)
                            else:
                                line +=  '-99\t-99\t-99\t'
                            #h.append(j[4:])
                            #h.append(j[4:])
                            #h.append(j[4:])
                        else:
                            line += '-99.9\t-99.9\t-99.9\t'
                            #h.append(j[4:])
                            #h.append(j[4:])
                            #h.append(j[4:])


                else:
                    for j in unique_PDF:
                        line += '-99.9\t-99.9\t-99.9\t'

                #print(unique_PDF, len(h)-4, h)
                if 'Parameters_BF' in list(obj.keys()):
                    listParam_BF = list(obj['Parameters_BF'].keys())
                    for j in unique_BF:
                        if j[3:] in listParam_BF:
                            P = numpy.array(obj['Parameters_BF/%s'%(j[3:])])
                            line += '%s\t'%round(numpy.ndarray.item(P),3)
                            #h.append(j[3:])
                        else:
                            #h.append(j[3:])
                            line += '-99.9\t'

                if 'Mag_abs' in list(obj.keys()):
                    for j in unique_mag:
                        M = numpy.array(obj['Mag_abs/%s'%(j)])
                        if M == numpy.nan:
                            line += '-99.9\t'
                            #h.append(j)
                        else:
                            line += '%s\t'%round(numpy.ndarray.item(M),3)
                            #h.append(j)
                 
            #print(h, len(headers), len(h))
        else:
            line = '%s\t-99.9\t-99.9\t'%i
            for j in headers[3:]:
                line += '-99.9\t'
                #h.append('NAN')

        line += '\n'
        cat.write(line)

    R.close()
    cat.close()
