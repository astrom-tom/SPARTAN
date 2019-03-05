.. _Photometry:


|python| |Python36| |Licence|
|matplotlib| |PyQt5| |numpy| |scipy| 

.. |Licence| image:: https://img.shields.io/badge/License-GPLv3-blue.svg
      :target: http://perso.crans.org/besson/LICENSE.html

.. |Opensource| image:: https://badges.frapsoft.com/os/v1/open-source.svg?v=103
      :target: https://github.com/ellerbrock/open-source-badges/

.. |python| image:: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
    :target: https://www.python.org/downloads/release/python-360/

.. |PyQt5| image:: https://img.shields.io/badge/poweredby-PyQt5-orange.svg
   :target: https://pypi.python.org/pypi/PyQt5

.. |matplotlib| image:: https://img.shields.io/badge/poweredby-matplotlib-orange.svg
   :target: https://matplotlib.org/

.. |Python36| image:: https://img.shields.io/badge/python-3.6-blue.svg
.. _Python36: https://www.python.org/downloads/release/python-360/

.. |numpy| image:: https://img.shields.io/badge/poweredby-numpy-orange.svg
   :target: http://www.numpy.org/

.. |scipy| image:: https://img.shields.io/badge/poweredby-scipy-orange.svg
   :target: https://www.scipy.org/


Photometric fitting
===================

Configuration
^^^^^^^^^^^^^

The catalog that you need to give to SPARTAN is an ascii file. When SPARTAN opens it, it will read the header. Whatever you want to fit the header of the catalog must start with two columns: ID and redshift with an hash(#) at the beginning of the line. THIS IS MANDATORY:

.. centered::
	#ident     redshift


Then you must add the columns with the following rules. When you want to fit multi wavelength photometry, you have to  add as many 2 columns sets as you have photometric points. Therefore you will have (for 5 photometric points):

.. centered:: 
 	#ident     redshift  mag1    mag1_err   mag2    mag2_err  mag3    mag3_err  mag4  mag4_err mag5 mag5_err


Fitting procedure: generalities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. figure:: ./flow_charts/Fit_spectro.png
    :width: 750px
    :align: center


The flow chart on the left show the detailed procedure of the fit of a sample of  single spectra. It is composed of 3 parts:

* The initialization of the run where we load the library and the sample to fit.
* The main loop. Where are actually making the fit
* The results module where we save the results of a fit and where the final catalog of parameter is created

We describe in detail each parts below in the following paragraphs.

The Initialization
------------------

Here SPARTAN load the library that was computed from the configuration of the user. It loads both the table of parameters (and their names) and the table of templates. Everything is loaded from the .hdf5 library file.
Then the code takes the _dat.hdf5 file that was created from the configuration and the catalog of data that was given. He will make a quick loop over the full sample to check if some objects were already fitted. If so they will be skipped (unless the user allow the overfit, c.f. configuration above and TUI.)


.. warning::
	 This first check is important. It means you can stop a fitting run at any moment and start it again from where you stopped, without needing to start all the run over from the beginning.  


From the left over objects to plot, SPARTAN will take the firsts Ncpu (see TUI) object in the list and will send them to the fitting function. Each object will be fitted in parallel.

The main function
-----------------



The result module
-----------------

From the library of chi2, SPARTAN computes the PDF and the CDF for each parameter (see statistic). This will give access to the parameter measurements and their errors. If the user ask for it, the parameters from the best fit template (therefore without error) can be saved as well (see below). Aditionnaly, SPARTAN saves the best fit template (both original and resampled templates).

Data/Template Normalization
^^^^^^^^^^^^^^^^^^^^^^^^^^^

As explained in (:doc:`photo`)


 
Results: Final catalog production and GUI vizualization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At the end of the fitting run, SPARTAN creates automatically the final catalog. Depending on what you asked for, it will contain:

* The ID, redshift and number of points used during the fitting run
* The PDF parameters (measurement and errors, ex: PDF_SFR, m1s_SFR, p1s_SFR)
* The Parameters from the best fit template (no errors in this case, ex: BF_SFR)

After the fit you can also load the result file into the SPARTAN GUI. This will allow you to visualize the individual fits (see below). It can also show you the global result of your sample. Go to the :doc:`GUI` GUI documentation for more information.
