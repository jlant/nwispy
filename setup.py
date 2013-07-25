try:
	from setuptools import setup, find_packages
except ImportError:
	from distutils.core import setup

with open('README.rst') as f:    
	readme = f.read()

with open('LICENSE.txt') as f:    
	license = f.read()	
	
setup(
	name = 'nwispy',
	version = '1.0.0',
	description = 'Read, process, print, and plot hydrologic data from USGS NWIS data files.',
	long_description = readme,
	author = 'Jeremiah Lant',
	author_email = 'jlant@usgs.gov',
	url = 'https://github.com/jlant-usgs/nwispy',
	license = license,
	packages = find_packages()
	)
