===================
**terminal-cam**
===================

.. image:: https://img.shields.io/badge/version-1.1.0.dev0-yellow.svg
   :target: https://github.com/TodoLodo/terminal-cam


----

**Terminal Cam** is a **python script** that captures frames from your webcam and prints them out to the terminal using relevant characters.

=============
Documentation
=============

Set-up
======

Install the requirement libraries using `pip`_:

.. code-block:: bash

    pip install -r requirements.txt

.. _pip: https://pip.pypa.io/en/stable/getting-started/

Usage
=====

**terminal-cam.py** is easy to use with couple of options ranging from 0 to 4 taken as arguments.

* option 0, will printout 12 types of characters depending the grayscale value at each points of downscaled frame (default)
* option 1, will be same as option 0 and characters will have a color respective to highest present color among red, green and blue

.. code-block:: bash

    py terminal-cam.py <option>


terminal resolution change will occur the printed frame to change in resolution accordingly.

Contribute
==========

Contributions are welcome for this project to add more features, fulfill feature requests, and fix bugs. Even if you're not fond of coding much, you may contribute by mentioning any issues, bugs, or even features you may hope to see in the future.

----------------------------------------------------------------------------------------------------------------------

`Buy Me A Coffee <https://www.buymeacoffee.com/todolodo2089>`_
