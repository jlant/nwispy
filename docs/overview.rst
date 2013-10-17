Overview
===========

**nwispy** is a project that contains a python module that reads, processes, plots, 
and allows query capability for USGS NWIS data files. The NWIS data file can be either 
a daily or instantaneous data file. The data file can contain any number of parameters; 
i.e. discharge, gage height, temperature, sediement concentration, etc. **nwispy** also 
contains a gui that allows users to interact and query a timeseries of a particular hydrologic 
parameter from a USGS NWIS.

This software is provisional. The intended use of the software is to analyze and process USGS 
NWIS data files.

Details
-------

In the *nwispy.py* module, *main()* prompts a user for an NWIS file, processes the file, 
prints NWIS file information to the console, and plots each parameter found within the 
data file. Plots are saved to a directory called 'figs' which is created in the same directory 
as the data file. A log file called 'nwis_error.log' is created if any errors are found in the 
data file, and is saved in the same directory as the data file. The 'nwis_error.log' file 
logs errors such as missing data and any erroneous parameter values contained in the file. 

*nwispygui.py* creates an interactive plot of an NWIS data file. User can interact with the plot
via a SpanSelector mouse widget. A toggle key event handler exists for the matplotlib SpanSelector 
widget. A keypress of 'A' or 'a' actives the slider and a keypress of 'Q' or 'q' de-activates the 
slider.
	
USGS NWIS data files can be found at: 

		http://waterdata.usgs.gov/nwis/rt

Author
------

Jeremiah Lant

jlant@usgs.gov

