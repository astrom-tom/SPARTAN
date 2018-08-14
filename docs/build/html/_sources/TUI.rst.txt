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
---------------------------------------------------------
---------------------------------------------------------

As said in :doc:`usage`, you start SPARTAN using the command line. Here we document the text based user interface that is used to configure a fitting run. For a brand new project, you start in the terminal:

.. code-block:: shell

           [user@machine]$ spartan - -tui (or -t)

This will load the text based user interface (TUI) with an empty project. If you happen to have an already defined project, you must precise the file that the TUI will use:

.. code-block:: shell

           [user@machine]$ spartan - -tui /path/and/file.conf

To make sure that the TUI is well displayed the size of your terminal must be at least 30x80. If this is the case, running one of the command above will lead you to the front frame of the TUI that you can see below.

.. figure:: ./TUI/TUI_front.png
    :width: 750px
    :align: center


