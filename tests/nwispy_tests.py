# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 15:05:27 2013

@author: jlant

Author: Jeremiah Lant
Email: jlant@usgs.gov
"""

import sys
import nose.tools
from nose import with_setup
from nose.tools import *
import datetime
import re
import nose

# my module
from nwispy import nwispy

# define the global fixture to hold the data that goes into the functions you test
fixture = {}

# define a setup function that runs BEFORE every test method
def setup():
    # this is how you print out to console
    print >> sys.stderr, "SETUP!"
    
    # set up fixture with possible date strings
    fixture['instantaneous_date'] = {'daily': '2013-06-25', 'instantaneous': '00:15\tEDT'}
    fixture['daily_date'] = {'daily': '2013-06-25', 'instantaneous': None}
    
    # set up fixture with possible parameter codes
    fixture['parameter_code'] = {   
		'pattern': '(#)\D+([0-9]{2})\D+([0-9]{5})(\D+[0-9]{5})?(.+)',
        'discharge_daily': '#    06   00060     00003     Discharge, cubic feet per second (Mean)',
        'discharge_instant': '#    02   00060     Discharge, cubic feet per second',
        'gage_height': '#    01   00065     Gage height, feet',
        'battery': '#    03   70969     DCP battery voltage, volts',
        'precip': '#    03   00045     Precipitation, total, inches',
        'sediment_concentration': '#    08   80154     00003     Suspended sediment concentration, milligrams per liter (Mean)',
        'sediment_discharge': '#    09   80155     00003     Suspended sediment discharge, tons per day (Mean)'
    }
    
# define a teardown function that runs AFTER every test method
def teardown():
    print >> sys.stderr, "TEAR DOWN!"

    fixture = {}    
	
#@with_setup(setup, teardown)
def test_instantaneous_date():
    
    expected = datetime.datetime(2013, 6, 25, 0, 15)
    
    actual = nwispy.get_date(daily = fixture['instantaneous_date']['daily'], instantaneous = fixture['instantaneous_date']['instantaneous'])

    nose.tools.assert_equals(actual, expected)

#@with_setup(setup, teardown)
def test_daily_date():
    
    expected = datetime.datetime(2013, 6, 25, 0, 0)
    
    actual = nwispy.get_date(daily = fixture['daily_date']['daily'], instantaneous = fixture['daily_date']['instantaneous'])

    nose.tools.assert_equals(actual, expected)
    
def test_parameter_code_discharge_daily():
    
    expected = ('06_00060_00003', 'Discharge, cubic feet per second (Mean)')    
    
    pattern_object = re.compile(fixture['parameter_code']['pattern']) 
    match = pattern_object.match(fixture['parameter_code']['discharge_daily'])
    
    actual = nwispy.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)
    
def test_parameter_code_discharge_instant():
    
    expected = ('02_00060', 'Discharge, cubic feet per second')    
    
    pattern_object = re.compile(fixture['parameter_code']['pattern']) 
    match = pattern_object.match(fixture['parameter_code']['discharge_instant'])
    
    actual = nwispy.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)
    
def test_parameter_code_gage_height():
    
    expected = ('01_00065', 'Gage height, feet')    
    
    pattern_object = re.compile(fixture['parameter_code']['pattern']) 
    match = pattern_object.match(fixture['parameter_code']['gage_height'])
    
    actual = nwispy.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)

def test_parameter_code_battery():
    
    expected = ('03_70969', 'DCP battery voltage, volts')    
    
    pattern_object = re.compile(fixture['parameter_code']['pattern']) 
    match = pattern_object.match(fixture['parameter_code']['battery'])
    
    actual = nwispy.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)

def test_parameter_code_precip():
    
    expected = ('03_00045', 'Precipitation, total, inches')    
    
    pattern_object = re.compile(fixture['parameter_code']['pattern']) 
    match = pattern_object.match(fixture['parameter_code']['precip'])
    
    actual = nwispy.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)

def test_parameter_code_sediment_concentration():
    
    expected = ('08_80154_00003', 'Suspended sediment concentration, milligrams per liter (Mean)')    
    
    pattern_object = re.compile(fixture['parameter_code']['pattern']) 
    match = pattern_object.match(fixture['parameter_code']['sediment_concentration'])
    
    actual = nwispy.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)
    
def test_parameter_code_sediment_discharge():
    
    expected = ('09_80155_00003', 'Suspended sediment discharge, tons per day (Mean)')    

    pattern_object = re.compile(fixture['parameter_code']['pattern']) 
    match = pattern_object.match(fixture['parameter_code']['sediment_discharge'])
    
    actual = nwispy.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)    