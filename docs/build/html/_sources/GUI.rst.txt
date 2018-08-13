.. _Usage:


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

Graphical User interface: Visualizing results
--------------------------------------------
---------------------------------------------
You start SPARTAN from a terminal. SPARTAN comes with a command line interface which includes a 'help' that you can display in your terminal using the help command. It must be called like this::

           [user@machine]$ spartan --help

This command will display the help of the program::

      usage: atacama [-h] [-p PROJECT] [-d] [--version]

      ATACAMA, R. Thomas, 2018, This program comes with ABSOLUTELY NO WARRANTY; and
      is distributed under the GPLv3.0 Licence terms.See the version of this Licence
      distributed along this code for details. website: 
      https://astrom-tom.github.io/ATACAMA/build/html/index.html

      optional arguments:
      -h, --help            Show this help message and exit
      -p PROJECT, --project PROJECT
                            Project file created by ATACAMA
      --drop                Will scroll the configuration area all the way down.
      --docs                Open the doc in web browser
      --verbose             Will display sextractor communication in terminal.
      --version             Display version of photon.

In details it means:

* ATACAMA has 6 optionnal arguments. You can start ATACAMA without any argument (and start an empty project) or use one (or more). 
* Few arguments can be used:
	
	* -h: Display this help in the terminal.
	* -p or --project: Takes an Atacama project file as input. Allows to load a previously created project. 
	* --drop: The configuration area (see below) will be scrolled all the way down. 
	* --docs: Display in the web browser the documentation of the code. If you have a valid internet connection it will open the online documentation, if not it will open the local documentation.
	* --version: Display in terminal the current version of the software.
	* --verbose: Will use the verbose mode of sextractor and display information in the terminal.

The command line interface is made using the argparse library (part of the standard python library).


