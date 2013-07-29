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
import numpy as np
import datetime
import re
import nose
from StringIO import StringIO

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

    fixture['data_daily_single_parameter'] = '''
        # ---------------------------------- WARNING ----------------------------------------
        # The data you have obtained from this automated U.S. Geological Survey database
        # have not received Director's approval and as such are provisional and subject to
        # revision.  The data are released on the condition that neither the USGS nor the
        # United States Government may be held liable for any damages resulting from its use.
        # Additional info: http://waterdata.usgs.gov/nwis/help/?provisional
        #
        # File-format description:  http://waterdata.usgs.gov/nwis/?tab_delimited_format_info
        # Automated-retrieval info: http://waterdata.usgs.gov/nwis/?automated_retrieval_info
        #
        # Contact:   gs-w_support_nwisweb@usgs.gov
        # retrieved: 2013-07-02 22:08:51 EDT       (sdww01)
        #
        # Data for the following 1 site(s) are contained in this file
        #    USGS 03290500 KENTUCKY RIVER AT LOCK 2 AT LOCKPORT, KY
        # -----------------------------------------------------------------------------------
        #
        # Data provided for site 03290500
        #    DD parameter statistic   Description
        #    06   00060     00003     Discharge, cubic feet per second (Mean)
        #
        # Data-value qualification codes included in this output: 
        #     A  Approved for publication -- Processing and review completed.  
        #     P  Provisional data subject to revision.  
        #     e  Value has been estimated.  
        # 
        agency_cd	site_no	datetime	06_00060_00003	06_00060_00003_cd
        5s	15s	20d	14n	10s
        USGS	03290500	2012-07-01	171	A
        USGS	03290500	2012-07-02	190	A
        USGS	03290500	2012-07-03	164	A
        '''
	
# define a teardown function that runs AFTER every test method
def teardown():
    print >> sys.stderr, "TEAR DOWN!"

    fixture = {}    

def test_daily_single_parameter():
    
    expected = {
        'date_retrieved': '2013-07-02',
        'gage_name': 'USGS 03290500 KENTUCKY RIVER AT LOCK 2 AT LOCKPORT, KY',
        'column_names': ['agency_cd', 'site_no', 'datetime', '06_00060_00003', '06_00060_00003_cd'],
        'parameters': [{
            'code': '06_00060_00003',
            'description': 'Discharge, cubic feet per second (Mean)',
            'index': 3,
            'data': np.array([171, 190, 164]),
            'mean': np.mean([171, 190, 164]),
            'max': np.max([171, 190, 164]),
            'min': np.min([171, 190, 164]),
        }],
        'dates': np.array([datetime.datetime(2012, 07, 01, 0, 0), datetime.datetime(2012, 07, 02, 0, 0), datetime.datetime(2012, 07, 03, 0, 0)]),    
        'timestep': 'daily'   
    }  
	
    fileobj = StringIO(fixture['data_daily_single_parameter'])
    actual = nwispy.read_nwis_in(fileobj)
	
    nose.tools.assert_equals(actual['date_retrieved'], expected['date_retrieved'])
    nose.tools.assert_equals(actual['gage_name'], expected['gage_name'])
    nose.tools.assert_equals(actual['column_names'], expected['column_names'])
    
    nose.tools.assert_equals(actual['parameters'][0]['code'], expected['parameters'][0]['code'])
    nose.tools.assert_equals(actual['parameters'][0]['description'], expected['parameters'][0]['description'])
    nose.tools.assert_equals(actual['parameters'][0]['index'], expected['parameters'][0]['index'])
    
    nose.tools.assert_almost_equals(actual['parameters'][0]['data'][0], expected['parameters'][0]['data'][0])
    nose.tools.assert_almost_equals(actual['parameters'][0]['data'][1], expected['parameters'][0]['data'][1])
    nose.tools.assert_almost_equals(actual['parameters'][0]['data'][2], expected['parameters'][0]['data'][2])
    
    nose.tools.assert_almost_equals(actual['parameters'][0]['mean'], expected['parameters'][0]['mean'])
    nose.tools.assert_almost_equals(actual['parameters'][0]['max'], expected['parameters'][0]['max'])
    nose.tools.assert_almost_equals(actual['parameters'][0]['min'], expected['parameters'][0]['min'])
        
    nose.tools.assert_equals(actual['timestep'], expected['timestep'])
	
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