.. _installation:

|Python36| |Licence| |numpy| |scipy| 

.. |Licence| image:: https://img.shields.io/badge/License-GPLv3-blue.svg
      :target: http://perso.crans.org/besson/LICENSE.html

.. |Opensource| image:: https://badges.frapsoft.com/os/v1/open-source.svg?v=103
      :target: https://github.com/ellerbrock/open-source-badges/

.. |Python36| image:: https://img.shields.io/badge/python-3.6-blue.svg
.. _Python36: https://www.python.org/downloads/release/python-360/

.. |numpy| image:: https://img.shields.io/badge/poweredby-numpy-orange.svg
   :target: http://www.numpy.org/

.. |scipy| image:: https://img.shields.io/badge/poweredby-scipy-orange.svg
   :target: https://www.scipy.org/


Installation
------------
------------

SPARTAN has started in python 3.6 and isnow developped in python 3.7. The following library are used:

* Numpy v1.16.0: Numerical python
* Scipy v1.2.0: Some useful function for spectral processing
* h5py  v2.9.0: hdf5 file creation and handling
* tqdm  v4.29.1: progress bar
* astropy v3.1.1: some useful astronomical functions
* catscii 1.1: catalog managing.
* npyscreen v4.10.5: Terminal based interface
* PyQt5 v5.11.3: Graphical Interface
* matplotlib 3.0.2: fit display in the GUI.


Other libraries are used but they are all part of the standard python library. As such no extra installations are needed.

The last SPARTAN version is v0.4.4 and allows for independent fir of photometry and spectroscopy. If you want to try a this version (that is already used in some papers in preparation) you can go in the *dist* directory in GITHUB and download the last version. Then you install it with 

.. code-block:: shell
     :linenos:

     pip install spartan.X.Y.Z.tar.gz --user 

Using this command will allow you not to have to install any other package. Pip will install what is missing for you.

