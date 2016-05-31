==================================================================
*interactiveTutorial* - fast and easy interactive tutorials for Qt
==================================================================

|GPLv3 License|
|Python 2.6\|2.7|
.. |GPLv3 License| image:: https://img.shields.io/badge/License-GPLv3-red.svg
.. |Python 2.6\|2.7| image:: https://img.shields.io/badge/python-2.6%7C2.7-yellow.svg :target: https://www.python.org/


Based on `PyQt4 <http://www.riverbankcomputing.co.uk/software/pyqt/download>`_.

- Browse the `API Documentation <http://radjkarl.github.io/interactiveTutorial>`_
- Fork the code on `github <https://github.com/radjkarl/interactiveTutorial>`_


.. image:: https://raw.githubusercontent.com/radjkarl/interactiveTutorial/master/interactiveTutorial_showcase.png
    :align: center
    :alt: showcase


Installation
^^^^^^^^^^^^

**interactiveTutorial** is listed in the Python Package Index. You can install it typing::

    pip install interactiveTutorial

Scope
^^^^^

Instead of a static PDF tutorial this package allows you to *run* and *create*
tutorials within your PyQt4 based application. Tutorials are created through choosing
a point of interest (POI), e.g. a widget, and typing an explaining text for each step.

Usage
^^^^^

**RunTutorial**

* widget to execute a given tutorial

**CreateTutorial**

* widget to create and edit tutorials

**TutorialMenu**

* QMenu listing all created tutorials and allowing to run and edit them.
* Embedd this one in your QMenuBar and you have all functionalities of **interactiveTutorial**

Issues
^^^^^^

* Instances of QMenu and QAction cannot be chosen as POI
* QWidgets within QTreeWidgetItems are only marked on focus

... if you find more´, please let me know!


Tests
^^^^^
**interactiveTutorial** uses mostly the 'one class/function per module' rule. Running each module as program, like::

    python -m interactiveTutorial.TutorialMenu.TutorialMenu

will execute the test case of this module.