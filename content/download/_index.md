+++
title = "Download"
url = "/download/"
listing = true
+++

Windows
=======

[Quasar-1.11.1-Miniforge-x86_64.exe](https://download.biolab.si/download/files/quasar/Quasar-1.11.1-Miniforge-x86_64.exe) - an
installer that can be used without administrative privileges (64 bit).

When updating, remove the older version first. If there are any problems, also remove the corresponding Miniconda/Minifore and reinstall.

The package includes Python 3.11.8,
Orange 3.38.1, Orange-Spectroscopy 0.8.1, Orange-SNOM 0.0.4,
numpy 1.26.4, scipy 1.13.1, scikit-learn 1.5.2.

This installer used to be based on Miniconda, but since Anaconda changed their licensing terms, we switched to Miniforge in 1.10.2.

macOS
=====

Quasar for Apple silicon
------------------------

[Quasar-1.11.1-Python3.11.8-arm64.dmg](https://download.biolab.si/download/files/quasar/Quasar-1.11.1-Python3.11.8-arm64.dmg)


Quasar for Intel
----------------

[Quasar-1.11.1-Python3.10.11-x86_64.dmg](https://download.biolab.si/download/files/quasar/Quasar-1.11.1-Python3.10.11-x86_64.dmg)

**Not sure which installer to select?** Click the Apple logo in the top-left corner of your screen, select About This Mac, and check the Chip or Processor field. If you see Apple, select the Orange for Apple Silicon installer. If you see Intel, select the Orange for Intel.

The package includes
Orange 3.38.1, Orange-Spectroscopy 0.8.1, Orange-SNOM 0.0.4,
numpy 1.26.4, scipy 1.13.1, scikit-learn 1.5.2.

Version archive
===============

If needed, you can download previous versions from our [download archive](https://download.biolab.si/download/files/quasar/).

Other platforms
===============

With pip
--------

On other platforms, such as Linux, you will need a fairly recent python3 installation.
We highly recommend that you create a python virtual environment first. 
There, install Quasar with pip:

    pip install quasar
    
The above command will install all dependencies except PyQt. Install it with

    pip install PyQt5

Then, run Quasar with:

    python -m quasar

To open Bruker OPUS files, also install opusFC (only available for some platforms):

    pip install opusFC

With conda
----------

If you are using python provided by conda (we recommend obtaining it with Miniforge), you are almost ready to go.

As with pip, we highly recommend you create a separate environment for your Quasar installation.

Add two new channels:

    conda config --add channels conda-forge
    conda config --add channels https://quasar.codes/conda/

and set the channel_priority recommended by [conda-forge](https://conda-forge.org/docs/user/tipsandtricks.html#how-to-fix-it):

    conda config --set channel_priority strict

and install the quasar package:

    conda install quasar

To open Bruker OPUS files, also install opusFC (only available for some platforms):

    conda install opusfc

