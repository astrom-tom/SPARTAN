.. _TUI:


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

Text Based User interface: configuration of a fitting run
=========================================================

Start the TUI
^^^^^^^^^^^^^

As said in :doc:`usage`, you start SPARTAN using the command line. Here we document the text based user interface that is used to configure a fitting run. For a brand new project, you start in the terminal:

.. code-block:: shell

           [user@machine]$ spartan -t (or --tui)

This will load the text based user interface (TUI) with an empty project. If you happen to have an already defined project, you must precise the file that the TUI will use:

.. code-block:: shell

           [user@machine]$ spartan -t /path/and/file.conf (or --tui)

To make sure that the TUI is well displayed the size of your terminal must be at least 30x80. If this is the case, running one of the command above will lead you to the front frame of the TUI that you can see below.

.. figure:: ./TUI/TUI_fron.png
    :width: 750px
    :align: center


To navigate through the TUI you need the arrow keys of your keyboard to move from on element to another and the carriage return to enter a new element. The space bar is used to select a choice in a multiple choice element (see below).

This frame contains the SPARTAN logo and the welcome message. These are fixed components. Then you haves an area with 6 entries: Project general Configuration, Spectroscopy, Photometry, Library, Cosmology, Fit & output. Each section corresponds to a TUI-frame that will help you through the configuration of your fitting run. On the same line as the section,  a keyword is displayed. If it is green (like for the Cosmology section in the screenshot above), it means that the section is correctly configured.  In green you can have  'Default' or 'Done'. Once each section status is in green you can start a fitting run. If you made a mistake during the configuration (or something is missing), the status will be displayed in red. The red status keywords should be clear enough by themselves. Each one will be reviewed in the next sections so you have a more detailed description of the error and a work around.

Below this sections you have a choice to start the fitting run from the TUI or not. Select your choise with the space bar. If you choose not to start it from the TUI you can still do it from the Command Line Interface.

Finally, to Leave the TUI you must go to the 'OK' at the bottom right and press enter.


General Configuration
^^^^^^^^^^^^^^^^^^^^^
