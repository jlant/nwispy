.. nwispy documentation master file, created by
   sphinx-quickstart on Wed Jul 24 20:37:09 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to nwispy's documentation!
================================

**nwispy** is a project that contains a python module that reads, processes, plots, 
and allows query capability for USGS NWIS data files. The NWIS data file can be either 
a daily or instantaneous data file. The data file can contain any number of parameters; 
i.e. discharge, gage height, temperature, sediement concentration, etc. **nwispy** also 
contains a gui that allows users to interact and query a timeseries of a particular hydrologic 
parameter from a USGS NWIS.

Contents:

.. toctree::
   :maxdepth: 2

   overview.rst
   code.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Screenshot of nwisgui.py
------------------------
.. image:: _static/nwispygui.png