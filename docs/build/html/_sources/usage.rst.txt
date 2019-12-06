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


Getting started
===============

.. Danger:: 
        
        **Input Files**

        SPARTAN relies on numerous input files that are pre-computed (e.g. stellar population, IGM extinction, etc). To make use of SPARTAN you must download them at this `link <https://drive.google.com/drive/folders/1AVjhedoHhyt_eKd9wvZ_4CtX9DLC5_Sk?usp=sharing>`_.
        These are not being computed on the fly which saves a lot of time in the fitting process.



Command Line Interface
^^^^^^^^^^^^^^^^^^^^^^

You start SPARTAN from a terminal. SPARTAN comes with a command line interface which includes a 'help' that you can display in your terminal using the help command. It must be called like this::

           [user@machine]$ spartan --help

.. Important::
        At the first startup of spartan, the code will ask you

        '' where are the input files located?, (give aboslute path)  ''

        To that question you must give the absolute path to the input files of SPARTAN (see *danger* note above). 


This command will display the help of the program::

      usage: sp_v1 [-h] [-f [FILE]] [-t [TUI]] [-c] [-fo [OBJ]] [-r] [-v] [-s]

      SPARTAN V1.0, R. Thomas, 2019, ESO, This program comes with ABSOLUTELY NO
      WARRANTY; and is distributed under the GPLv3.0 Licence terms. See the version
      of this Licence distributed along this code for details.

      optional arguments:
       -h, --help            show this help message and exit
       -f [FILE], --file [FILE]
                        Configuration file. If no arg, the SPARTAN template
                        will be taken
       -t [TUI], --tui [TUI]
                        start SPARTAN configuration TUI. Default config file
                        is the SPARTAN configuration template
       -c, --check      Check Configuration file, need a completed
                        configuration file from the -f command
       -fo [OBJ], --OBJ [OBJ]
                        Display on the terminal the informations about one
                        object in you data. Need a completed configuration
                        file from the -f command
       -r, --run        Start the fitting process, need a completed
                        configuration file from the -f command
       -v, --visua      Load the SPARTAN-GUI to visualize the results,need a
                        completed configuration file from the -f command
       --docs           Open the documentation in web browser
       --version        Display in terminal the current version of SPARTAN


SPARTAN has 8 optionnal arguments. You **can not** start SPARTAN without any argument. 
Few arguments can be used:	

 * -h: Display this help in the terminal.
 * -f or --file + file.conf: This is used when you already have a SPARTAN configuration file ready.  
 * -t or --tui: This will display, in the terminal, the text-based interface. This helps you to configurate a fitting project. If you do not use it with '-f', it will load an empty project file.
 * -c or -- check: **To be used after '-f'**. This checks the configuration of the configuration file you give with '-f'
 * -r or --run: **To be used after '-f'**. This tells SPARTAN to start the fit with the project file you give using the '-f' argument 
 * -v or --visua: **To be used after '-f'**. This open the graphical interface to display all the result of a given fit.
 * -fo or --OBJ + object ID: **To be used after '-f'**. This look on the result file and give you the results for a given object.
 * - -docs: Will display the documentation of SPARTAN in browser.
 * - -version: It will display the version of SPARTAN you are using.

The command line interface is made using the argparse library (part of the standard python library).



Terminal User Interface
^^^^^^^^^^^^^^^^^^^^^^^

To configure a fitting run, you have to configure it. To do so you have to choices:
* Filling directly the configuration file
* Using the Text Based User Interface (TUI) to help you configure it. This interface is displayted in the terminal. You can find a proper documentation in the TUI dedicated page (:doc:`TUI`).


Graphical User Interface
^^^^^^^^^^^^^^^^^^^^^^^^

When a fitting run is done, you can visualize results using the graphical user interface that has been made for that. You can have a look at the GUI documentation page: :doc:`GUI`.
