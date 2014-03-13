nwispy
======

**Version**
1.0.0

![](images/nwispygui.png)

**DESCRIPTION**	

	nwispy is a repository for code that reads, processes, plots, and allows query capability 
	for USGS NWIS data files.

	*nwispy.py* is a module that contains functions to read, print, and plot data from an USGS 
	NWIS data file. The NWIS data file can be either a daily or instantaneous data file. The 
	data file can contain any number of parameters; i.e. discharge, gage height, temperature, 
	sediement concentration, etc.
	
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

	This software is provisional. The intended use of the software is to analyze and process USGS 
	NWIS data files.

**REQUIREMENTS**

	Please see requirements.txt
	
**INSTALLATION INSTRUCTIONS**

**DIRECTORY LAYOUT**

	bin/					# directory containing executables
	data/					# directory containing sample data files to use with software and associated information
		datafiles/			# directory containing sample data to use with software
			...
		README.txt			# file describing sample data in datafiles/
	docs/					# directory containing code documentation
		...
		html/				# html code documentation
		...
	nwispy/					# directory containing code package(s) or module(s)
		...
	tests/					# directory containing unit tests using *nose* library (https://nose.readthedocs.org/en/latest/)
		...
	LICENSE.txt				# USGS Software User Rights Notice
	README.md				# README file
	requirements.txt		# list of requirements/dependencies 
	setup.py				# code for building, distributing, and installing modules
	
**GENERAL INSTRUCTIONS**
	
**AUTHORS**

	Jeremiah Lant
	Hydrologist 
	U.S. Geological Survey
	Kentucky Water Science Center
	Louisville, Kentucky 40299
	jlant@ugs.gov
	
**DISCLAIMER and NOTICE**

	Please refer to the USGS Software User Rights Notice (LICENSE.txt or http://water.usgs.gov/software/help/notice/)
	for complete use, copyright, and distribution information. The USGS provides no warranty, expressed or implied, as to the
	correctness of the furnished software or the suitability for any purpose. The software has been tested, but as with any
	complex software, there could be undetected errors. Users who find errors are requested to report them to the USGS.

	References to non-USGS products, trade names, and (or) services are provided for information purposes only and do not
	constitute endorsement or warranty, express or implied, by the USGS, U.S. Department of Interior, or U.S. Government, as to
	their suitability, content, usefulness, functioning, completeness, or accuracy.

	Although this program has been used by the USGS, no warranty, expressed or implied, is made by the USGS or the United
	States Government as to the accuracy and functioning of the program and related program material nor shall the fact of
	distribution constitute any such warranty, and no responsibility is assumed by the USGS in connection therewith.
