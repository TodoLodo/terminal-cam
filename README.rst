===================
**terminal-cam**
===================

v1.0.2dev

------------------------------------------------------------------------------------------------------------------------

**Terminal Cam** is a **python script** which grabs the frames from your webcam and prints out to the terminal with relevant character

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
* option 1, will be same as option 0 but would print with different colors randomly chosen at each frame
* option 2, will be same as option 0 but would print randomly chosen color for bright spots at each frame
* option 3, will be the same as option 2 but colors will be randomised at each line
* option 4, will be same as option 0 but would detect one face and have random colors for the face at each frame

.. code-block:: bash

    py terminal-cam.py <option>


terminal resolution change will occur the printed frame to change in resolution accordingly.

Contribute
==========

Contributions are open for this project to add more features, full fill feature requests and fix bugs.
Even if your not fond of coding much you may contribute by mentioning any issues, bugs or even features you may hope to see in the future.

----------------------------------------------------------------------------------------------------------------------

`Buy Me A Coffee <https://www.buymeacoffee.com/todolodo2089>`_
