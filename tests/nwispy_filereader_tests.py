import nose.tools

import sys
import numpy as np
import datetime
import re
from StringIO import StringIO

# my module
from nwispy import nwispy_filereader

# define the global fixture to hold the data that goes into the functions you test
fixture = {}

def setup():
    """ Setup and initialize fixture for testing """

    print >> sys.stderr, "SETUP: nwispy_filereader tests"
   
    # set up fixture with possible date strings
    fixture["instantaneous_date"] = {"daily": "2013-06-25", "instantaneous": "00:15\tEDT"}
    fixture["daily_date"] = {"daily": "2013-06-25", "instantaneous": None}
    
    # set up fixture with possible parameter codes
    fixture["parameter_code"] = {   
		"pattern": "(#)\D+([0-9]{2})\D+([0-9]{5})(\D+[0-9]{5})?(.+)",
        "discharge_daily": "#    06   00060     00003     Discharge, cubic feet per second (Mean)",
        "discharge_instant": "#    02   00060     Discharge, cubic feet per second",
        "gage_height": "#    01   00065     Gage height, feet",
        "battery": "#    03   70969     DCP battery voltage, volts",
        "precip": "#    03   00045     Precipitation, total, inches",
        "sediment_concentration": "#    08   80154     00003     Suspended sediment concentration, milligrams per liter (Mean)",
        "sediment_discharge": "#    09   80155     00003     Suspended sediment discharge, tons per day (Mean)"
    }

    # set up fixture with sample data files
    fixture["data_daily_single_parameter"] = \
        """
        # ---------------------------------- WARNING ----------------------------------------
        # The data you have obtained from this automated U.S. Geological Survey database
        # have not received Director"s approval and as such are provisional and subject to
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
        USGS	03290500	2012-07-04	150	A
        USGS	03290500	2012-07-05	125	A
        """

    # set up fixture with sample data files
    fixture["data_instantaneous_single_parameter"] = \
        """
        # ---------------------------------- WARNING ----------------------------------------
        # The data you have obtained from this automated U.S. Geological Survey database
        # have not received Director"s approval and as such are provisional and subject to
        # revision.  The data are released on the condition that neither the USGS nor the
        # United States Government may be held liable for any damages resulting from its use.
        # Additional info: http://nwis.waterdata.usgs.gov/ca/nwis/?provisional
        #
        # File-format description:  http://nwis.waterdata.usgs.gov/nwis/?tab_delimited_format_info
        # Automated-retrieval info: http://nwis.waterdata.usgs.gov/nwis/?automated_retrieval_info
        #
        # Contact:   gs-w_support_nwisweb@usgs.gov
        # retrieved: 2014-03-13 17:19:26 EDT       (nadww01)
        #
        # Data for the following 1 site(s) are contained in this file
        #    USGS 11143000 BIG SUR R NR BIG SUR CA
        # -----------------------------------------------------------------------------------
        #
        # Data provided for site 11143000
        #    DD parameter   Description
        #    03   00065     Gage height, feet
        #
        # Data-value qualification codes included in this output: 
        #     A  Approved for publication -- Processing and review completed.  
        #     P  Provisional data subject to revision.  
        # 
        agency_cd	site_no	datetime	tz_cd	03_00065	03_00065_cd
        5s	15s	20d	6s	14n	10s
        USGS	11143000	2010-03-01 00:00	PST	5.0	A
        USGS	11143000	2010-03-01 00:15	PST	10.0	A
        USGS	11143000	2010-03-01 00:30	PST	15.0	A
        USGS	11143000	2010-03-01 00:45	PST	4.5	A
        USGS	11143000	2010-03-01 01:00	PST	5.5	A
        """

    # set up fixture with sample data files
    fixture["data_instantaneous_multi_parameter"] = \
        """
        # ---------------------------------- WARNING ----------------------------------------
        # The data you have obtained from this automated U.S. Geological Survey database
        # have not received Director"s approval and as such are provisional and subject to
        # revision.  The data are released on the condition that neither the USGS nor the
        # United States Government may be held liable for any damages resulting from its use.
        # Additional info: http://nwis.waterdata.usgs.gov/ky/nwis/?provisional
        #
        # File-format description:  http://nwis.waterdata.usgs.gov/nwis/?tab_delimited_format_info
        # Automated-retrieval info: http://nwis.waterdata.usgs.gov/nwis/?automated_retrieval_info
        #
        # Contact:   gs-w_support_nwisweb@usgs.gov
        # retrieved: 2014-03-11 08:40:40 EDT       (nadww01)
        #
        # Data for the following 1 site(s) are contained in this file
        #    USGS 03401385 DAVIS BRANCH AT HIGHWAY 988 NEAR MIDDLESBORO, KY
        # -----------------------------------------------------------------------------------
        #
        # Data provided for site 03401385
        #    DD parameter   Description
        #    02   00065     Gage height, feet
        #    03   00010     Temperature, water, degrees Celsius
        #    04   00300     Dissolved oxygen, water, unfiltered, milligrams per liter
        #    05   00400     pH, water, unfiltered, field, standard units
        #    06   00095     Specific conductance, water, unfiltered, microsiemens per centimeter at 25 degrees Celsius
        #    07   63680     Turbidity, water, unfiltered, monochrome near infra-red LED light, 780-900 nm, detection angle 90 +-2.5 degrees, formazin nephelometric units (FNU)
        #
        # Data-value qualification codes included in this output: 
        #     Eqp  Equipment malfunction  
        #     P  Provisional data subject to revision.  
        #     ~  Value is a system interpolated value.  
        # 
        agency_cd	site_no	datetime	tz_cd	02_00065	02_00065_cd	03_00010	03_00010_cd	04_00300	04_00300_cd	05_00400	05_00400_cd	06_00095	06_00095_cd	07_63680	07_63680_cd
        5s	15s	20d	6s	14n	10s	14n	10s	14n	10s	14n	10s	14n	10s	14n	10s
        USGS	03401385	2013-06-06 00:00	EDT	1.0	P	5.0	P	2.0	P	-4.0	P	2.0	P	8.25	P
        USGS	03401385	2013-06-06 00:15	EDT	2.0	P	10.0	P	1.25	P	4.0	P	1.0	P	8.25	P
        USGS	03401385	2013-06-06 00:30	EDT	3.0	P	15.0	P	1.25	P	3.5	P	0.0	P	3.5	P
        USGS	03401385	2013-06-06 00:45	EDT	4.0	P	20.0	P	0.25	P	3.5	P	-1.0	P	2.5	P
        USGS	03401385	2013-06-06 01:00	EDT	5.0	P	25.0	P	0.25	P	3.0	P	-2.0	P	2.5	P
        """

    # set up fixture with sample data files
    fixture["bad_data_daily_single_parameter"] = \
        """
        # ---------------------------------- WARNING ----------------------------------------
        # The data you have obtained from this automated U.S. Geological Survey database
        # have not received Director"s approval and as such are provisional and subject to
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
        USGS	03290500	2012-07-01	171_	A
        USGS	03290500	2012-07-02	190_	A
        USGS	03290500	2012-07-03	164_	A
        USGS	03290500	2012-07-04	150_	A
        USGS	03290500	2012-07-05	125_	A
        """

    # set up fixture with sample data files
    fixture["bad_data_instantaneous_single_parameter1"] = \
        """
        # ---------------------------------- WARNING ----------------------------------------
        # The data you have obtained from this automated U.S. Geological Survey database
        # have not received Director"s approval and as such are provisional and subject to
        # revision.  The data are released on the condition that neither the USGS nor the
        # United States Government may be held liable for any damages resulting from its use.
        # Additional info: http://nwis.waterdata.usgs.gov/ca/nwis/?provisional
        #
        # File-format description:  http://nwis.waterdata.usgs.gov/nwis/?tab_delimited_format_info
        # Automated-retrieval info: http://nwis.waterdata.usgs.gov/nwis/?automated_retrieval_info
        #
        # Contact:   gs-w_support_nwisweb@usgs.gov
        # retrieved: 2014-03-13 17:19:26 EDT       (nadww01)
        #
        # Data for the following 1 site(s) are contained in this file
        #    USGS 11143000 BIG SUR R NR BIG SUR CA
        # -----------------------------------------------------------------------------------
        #
        # Data provided for site 11143000
        #    DD parameter   Description
        #    03   00065     Gage height, feet
        #
        # Data-value qualification codes included in this output: 
        #     A  Approved for publication -- Processing and review completed.  
        #     P  Provisional data subject to revision.  
        # 
        agency_cd	site_no	datetime	tz_cd	03_00065	03_00065_cd
        5s	15s	20d	6s	14n	10s
        USGS	11143000	2010-03-01 00:00	PST	5.0	A
        USGS	11143000	2010-03-01 00:15	PST	10.0	A
        USGS	11143000	2010-03-01 00:30	PST		A
        USGS	11143000	2010-03-01 00:45	PST		A
        USGS	11143000	2010-03-01 01:00	PST	5.5	A
        """

    fixture["bad_data_instantaneous_single_parameter2"] = \
        """
        # ---------------------------------- WARNING ----------------------------------------
        # The data you have obtained from this automated U.S. Geological Survey database
        # have not received Director"s approval and as such are provisional and subject to
        # revision.  The data are released on the condition that neither the USGS nor the
        # United States Government may be held liable for any damages resulting from its use.
        # Additional info: http://nwis.waterdata.usgs.gov/ca/nwis/?provisional
        #
        # File-format description:  http://nwis.waterdata.usgs.gov/nwis/?tab_delimited_format_info
        # Automated-retrieval info: http://nwis.waterdata.usgs.gov/nwis/?automated_retrieval_info
        #
        # Contact:   gs-w_support_nwisweb@usgs.gov
        # retrieved: 2014-03-13 17:19:26 EDT       (nadww01)
        #
        # Data for the following 1 site(s) are contained in this file
        #    USGS 11143000 BIG SUR R NR BIG SUR CA
        # -----------------------------------------------------------------------------------
        #
        # Data provided for site 11143000
        #    DD parameter   Description
        #    03   00065     Gage height, feet
        #
        # Data-value qualification codes included in this output: 
        #     A  Approved for publication -- Processing and review completed.  
        #     P  Provisional data subject to revision.  
        # 
        agency_cd	site_no	datetime	tz_cd	03_00065	03_00065_cd
        5s	15s	20d	6s	14n	10s
        USGS	11143000	2010-03-01 00:00	PST	Ice	A
        USGS	11143000	2010-03-01 00:15	PST	Ice	A
        USGS	11143000	2010-03-01 00:30	PST	*	A
        USGS	11143000	2010-03-01 00:45	PST	*	A
        USGS	11143000	2010-03-01 01:00	PST	50.0	A
        """


def teardown():
    """ Print to standard error when all tests are finished """
    
    print >> sys.stderr, "TEARDOWN: nwispy_filereader tests"      


def test_instantaneous_date():
    
    expected = datetime.datetime(2013, 6, 25, 0, 15)
    
    actual = nwispy_filereader.get_date(daily = fixture["instantaneous_date"]["daily"], instantaneous = fixture["instantaneous_date"]["instantaneous"])

    nose.tools.assert_equals(actual, expected)


def test_daily_date():
    
    expected = datetime.datetime(2013, 6, 25, 0, 0)
    
    actual = nwispy_filereader.get_date(daily = fixture["daily_date"]["daily"], instantaneous = fixture["daily_date"]["instantaneous"])

    nose.tools.assert_equals(actual, expected)
    
def test_parameter_code_discharge_daily():
    
    expected = ("06_00060_00003", "Discharge, cubic feet per second (Mean)")    
    
    pattern_object = re.compile(fixture["parameter_code"]["pattern"]) 
    match = pattern_object.match(fixture["parameter_code"]["discharge_daily"])
    
    actual = nwispy_filereader.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)
    
def test_parameter_code_discharge_instant():
    
    expected = ("02_00060", "Discharge, cubic feet per second")    
    
    pattern_object = re.compile(fixture["parameter_code"]["pattern"]) 
    match = pattern_object.match(fixture["parameter_code"]["discharge_instant"])
    
    actual = nwispy_filereader.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)
    
def test_parameter_code_gage_height():
    
    expected = ("01_00065", "Gage height, feet")    
    
    pattern_object = re.compile(fixture["parameter_code"]["pattern"]) 
    match = pattern_object.match(fixture["parameter_code"]["gage_height"])
    
    actual = nwispy_filereader.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)

def test_parameter_code_battery():
    
    expected = ("03_70969", "DCP battery voltage, volts")    
    
    pattern_object = re.compile(fixture["parameter_code"]["pattern"]) 
    match = pattern_object.match(fixture["parameter_code"]["battery"])
    
    actual = nwispy_filereader.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)

def test_parameter_code_precip():
    
    expected = ("03_00045", "Precipitation, total, inches")    
    
    pattern_object = re.compile(fixture["parameter_code"]["pattern"]) 
    match = pattern_object.match(fixture["parameter_code"]["precip"])
    
    actual = nwispy_filereader.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)

def test_parameter_code_sediment_concentration():
    
    expected = ("08_80154_00003", "Suspended sediment concentration, milligrams per liter (Mean)")    
    
    pattern_object = re.compile(fixture["parameter_code"]["pattern"]) 
    match = pattern_object.match(fixture["parameter_code"]["sediment_concentration"])
    
    actual = nwispy_filereader.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)
    
def test_parameter_code_sediment_discharge():
    
    expected = ("09_80155_00003", "Suspended sediment discharge, tons per day (Mean)")    

    pattern_object = re.compile(fixture["parameter_code"]["pattern"]) 
    match = pattern_object.match(fixture["parameter_code"]["sediment_discharge"])
    
    actual = nwispy_filereader.get_parameter_code(match)

    nose.tools.assert_equals(actual, expected)  


def test_daily_single_parameter():

    dates = np.array([datetime.datetime(2012, 07, 01, 0, 0), 
                      datetime.datetime(2012, 07, 02, 0, 0), 
                      datetime.datetime(2012, 07, 03, 0, 0),
                      datetime.datetime(2012, 07, 04, 0, 0),
                      datetime.datetime(2012, 07, 05, 0, 0),
    ])
    
    data = np.array([171, 190, 164, 150, 125])
    
    expected = {
        "date_retrieved": "2013-07-02 22:08:51",
        "gage_name": "USGS 03290500 KENTUCKY RIVER AT LOCK 2 AT LOCKPORT, KY",
        "column_names": ["agency_cd", "site_no", "datetime", "06_00060_00003", "06_00060_00003_cd"],
        "parameters": [{
            "code": "06_00060_00003",
            "description": "Discharge, cubic feet per second (Mean)",
            "index": 3,
            "data": data,
            "mean": np.mean(data),
            "max": np.max(data),
            "min": np.min(data),
        }],
        "dates": dates,    
        "timestep": "daily"   
    }  
	
    fileobj = StringIO(fixture["data_daily_single_parameter"])
    actual = nwispy_filereader.read_file_in(filestream = fileobj)
	
    nose.tools.assert_equals(actual["date_retrieved"], expected["date_retrieved"])
    nose.tools.assert_equals(actual["gage_name"], expected["gage_name"])
    nose.tools.assert_equals(actual["column_names"], expected["column_names"])
    
    nose.tools.assert_equals(actual["parameters"][0]["code"], expected["parameters"][0]["code"])
    nose.tools.assert_equals(actual["parameters"][0]["description"], expected["parameters"][0]["description"])
    nose.tools.assert_equals(actual["parameters"][0]["index"], expected["parameters"][0]["index"])

    nose.tools.assert_almost_equals(actual["parameters"][0]["data"].all(), expected["parameters"][0]["data"].all())    
       
    nose.tools.assert_almost_equals(actual["parameters"][0]["mean"], expected["parameters"][0]["mean"])
    nose.tools.assert_almost_equals(actual["parameters"][0]["max"], expected["parameters"][0]["max"])
    nose.tools.assert_almost_equals(actual["parameters"][0]["min"], expected["parameters"][0]["min"])

    nose.tools.assert_equals(actual["dates"].all(), expected["dates"].all())

    nose.tools.assert_equals(actual["timestep"], expected["timestep"])

def test_data_instantaneous_single_parameter():

    dates = np.array([datetime.datetime(2010, 03, 01, 0, 0), 
                      datetime.datetime(2010, 03, 01, 0, 15), 
                      datetime.datetime(2010, 03, 01, 0, 30),
                      datetime.datetime(2010, 03, 01, 0, 45),
                      datetime.datetime(2010, 03, 01, 1, 00),
    ])
    
    data = np.array([5.0, 10.0, 15.0, 4.5, 5.5])
    
    expected = {
        "date_retrieved": "2014-03-13 17:19:26",
        "gage_name": "USGS 11143000 BIG SUR R NR BIG SUR CA",
        "column_names": ["agency_cd", "site_no", "datetime", "tz_cd", "03_00065", "03_00065_cd"],
        "parameters": [{
            "code": "03_00065",
            "description": "Gage height, feet",
            "index": 4,
            "data": data,
            "mean": np.mean(data),
            "max": np.max(data),
            "min": np.min(data),
        }],
        "dates": dates,    
        "timestep": "instantaneous"   
    }  
	
    fileobj = StringIO(fixture["data_instantaneous_single_parameter"])
    actual = nwispy_filereader.read_file_in(filestream = fileobj)
	
    nose.tools.assert_equals(actual["date_retrieved"], expected["date_retrieved"])
    nose.tools.assert_equals(actual["gage_name"], expected["gage_name"])
    nose.tools.assert_equals(actual["column_names"], expected["column_names"])
    
    nose.tools.assert_equals(actual["parameters"][0]["code"], expected["parameters"][0]["code"])
    nose.tools.assert_equals(actual["parameters"][0]["description"], expected["parameters"][0]["description"])
    nose.tools.assert_equals(actual["parameters"][0]["index"], expected["parameters"][0]["index"])

    nose.tools.assert_almost_equals(actual["parameters"][0]["data"].all(), expected["parameters"][0]["data"].all())
    
    nose.tools.assert_almost_equals(actual["parameters"][0]["mean"], expected["parameters"][0]["mean"])
    nose.tools.assert_almost_equals(actual["parameters"][0]["max"], expected["parameters"][0]["max"])
    nose.tools.assert_almost_equals(actual["parameters"][0]["min"], expected["parameters"][0]["min"])

    nose.tools.assert_equals(actual["dates"].all(), expected["dates"].all())
        
    nose.tools.assert_equals(actual["timestep"], expected["timestep"])    

def test_data_instantaneous_multi_parameter():

    dates = np.array([datetime.datetime(2013, 06, 06, 0, 0), 
                      datetime.datetime(2013, 06, 06, 0, 15), 
                      datetime.datetime(2013, 06, 06, 0, 30),
                      datetime.datetime(2013, 06, 06, 0, 45),
                      datetime.datetime(2013, 06, 06, 1, 00),
    ])
    
    stage_data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    temperature_data = np.array([5.0, 10.0, 15.0, 20.0, 25.0])
    dissolved_oxygen_data = np.array([2.0, 1.25, 1.25, 0.25, 0.25])
    ph_data = np.array([-4.0, 4.0, 3.5, 3.5, 3.0])
    conductance_data = np.array([2.0, 1.0, 0.0, -1.0, -2.0])
    turbidity_data = np.array([8.25, 8.25, 3.5, 2.5, 2.5])
    
    expected = {
        "date_retrieved": "2014-03-11 08:40:40",
        "gage_name": "USGS 03401385 DAVIS BRANCH AT HIGHWAY 988 NEAR MIDDLESBORO, KY",
        "column_names": ["agency_cd", "site_no", "datetime", "tz_cd", "02_00065", "02_00065_cd", "03_00010", "03_00010_cd", "04_00300", "04_00300_cd", "05_00400", "05_00400_cd", "06_00095", "06_00095_cd", "07_63680", "07_63680_cd"],
        "parameters": [
            {
            "code": "02_00065",
            "description": "Gage height, feet",
            "index": 4,
            "data": stage_data,
            "mean": np.mean(stage_data),
            "max": np.max(stage_data),
            "min": np.min(stage_data),
            },
            {
            "code": "03_00010",
            "description": "Temperature, water, degrees Celsius",
            "index": 6,
            "data": temperature_data,
            "mean": np.mean(temperature_data),
            "max": np.max(temperature_data),
            "min": np.min(temperature_data),
            },
            {
            "code": "04_00300",
            "description": "Dissolved oxygen, water, unfiltered, milligrams per liter",
            "index": 6,
            "data": dissolved_oxygen_data,
            "mean": np.mean(dissolved_oxygen_data),
            "max": np.max(dissolved_oxygen_data),
            "min": np.min(dissolved_oxygen_data),
            },
            {
            "code": "05_00400",
            "description": "pH, water, unfiltered, field, standard units",
            "index": 8,
            "data": ph_data,
            "mean": np.mean(ph_data),
            "max": np.max(ph_data),
            "min": np.min(ph_data),
            },
            {
            "code": "06_00095",
            "description": "Specific conductance, water, unfiltered, microsiemens per centimeter at 25 degrees Celsius",
            "index": 10,
            "data": conductance_data,
            "mean": np.mean(conductance_data),
            "max": np.max(conductance_data),
            "min": np.min(conductance_data),
            },
            {
            "code": "07_63680",
            "description": "Turbidity, water, unfiltered, monochrome near infra-red LED light, 780-900 nm, detection angle 90 +-2.5 degrees, formazin nephelometric units (FNU)",
            "index": 12,
            "data": turbidity_data,
            "mean": np.mean(turbidity_data),
            "max": np.max(turbidity_data),
            "min": np.min(turbidity_data),
            },            
        ],
        "dates": dates,    
        "timestep": "instantaneous"   
    }  
	
    fileobj = StringIO(fixture["data_instantaneous_multi_parameter"])
    actual = nwispy_filereader.read_file_in(filestream = fileobj)
	
    nose.tools.assert_equals(actual["date_retrieved"], expected["date_retrieved"])
    nose.tools.assert_equals(actual["gage_name"], expected["gage_name"])
    nose.tools.assert_equals(actual["column_names"], expected["column_names"])
    
    nose.tools.assert_equals(actual["parameters"][0]["code"], expected["parameters"][0]["code"])
    nose.tools.assert_equals(actual["parameters"][0]["description"], expected["parameters"][0]["description"])
    nose.tools.assert_equals(actual["parameters"][0]["index"], expected["parameters"][0]["index"])

    nose.tools.assert_almost_equals(actual["parameters"][0]["data"].all(), expected["parameters"][0]["data"].all())
    nose.tools.assert_almost_equals(actual["parameters"][1]["data"].all(), expected["parameters"][1]["data"].all())
    nose.tools.assert_almost_equals(actual["parameters"][2]["data"].all(), expected["parameters"][2]["data"].all())
    nose.tools.assert_almost_equals(actual["parameters"][3]["data"].all(), expected["parameters"][3]["data"].all())
    nose.tools.assert_almost_equals(actual["parameters"][4]["data"].all(), expected["parameters"][4]["data"].all())
    nose.tools.assert_almost_equals(actual["parameters"][5]["data"].all(), expected["parameters"][5]["data"].all())
        
    
    nose.tools.assert_almost_equals(actual["parameters"][0]["mean"], expected["parameters"][0]["mean"])
    nose.tools.assert_almost_equals(actual["parameters"][0]["max"], expected["parameters"][0]["max"])
    nose.tools.assert_almost_equals(actual["parameters"][0]["min"], expected["parameters"][0]["min"])

    nose.tools.assert_almost_equals(actual["parameters"][1]["mean"], expected["parameters"][1]["mean"])
    nose.tools.assert_almost_equals(actual["parameters"][1]["max"], expected["parameters"][1]["max"])
    nose.tools.assert_almost_equals(actual["parameters"][1]["min"], expected["parameters"][1]["min"])

    nose.tools.assert_almost_equals(actual["parameters"][2]["mean"], expected["parameters"][2]["mean"])
    nose.tools.assert_almost_equals(actual["parameters"][2]["max"], expected["parameters"][2]["max"])
    nose.tools.assert_almost_equals(actual["parameters"][2]["min"], expected["parameters"][2]["min"])

    nose.tools.assert_almost_equals(actual["parameters"][3]["mean"], expected["parameters"][3]["mean"])
    nose.tools.assert_almost_equals(actual["parameters"][3]["max"], expected["parameters"][3]["max"])
    nose.tools.assert_almost_equals(actual["parameters"][3]["min"], expected["parameters"][3]["min"])

    nose.tools.assert_almost_equals(actual["parameters"][4]["mean"], expected["parameters"][4]["mean"])
    nose.tools.assert_almost_equals(actual["parameters"][4]["max"], expected["parameters"][4]["max"])
    nose.tools.assert_almost_equals(actual["parameters"][4]["min"], expected["parameters"][4]["min"])

    nose.tools.assert_almost_equals(actual["parameters"][5]["mean"], expected["parameters"][5]["mean"])
    nose.tools.assert_almost_equals(actual["parameters"][5]["max"], expected["parameters"][5]["max"])
    nose.tools.assert_almost_equals(actual["parameters"][5]["min"], expected["parameters"][5]["min"])

    nose.tools.assert_equals(actual["dates"].all(), expected["dates"].all())
         
    nose.tools.assert_equals(actual["timestep"], expected["timestep"]) 
    
    
def test_bad_daily_single_parameter():
    
    data = np.array([171, 190, 164, 150, 125])
    
    expected = {
        "parameters": [{
            "code": "06_00060_00003",
            "description": "Discharge, cubic feet per second (Mean)",
            "index": 3,
            "data": data,
            "mean": np.mean(data),
            "max": np.max(data),
            "min": np.min(data),
        }],
    }  
	
    fileobj = StringIO(fixture["data_daily_single_parameter"])
    actual = nwispy_filereader.read_file_in(filestream = fileobj)

    nose.tools.assert_almost_equals(actual["parameters"][0]["data"].all(), expected["parameters"][0]["data"].all())
    
    nose.tools.assert_almost_equals(actual["parameters"][0]["mean"], expected["parameters"][0]["mean"])
    nose.tools.assert_almost_equals(actual["parameters"][0]["max"], expected["parameters"][0]["max"])
    nose.tools.assert_almost_equals(actual["parameters"][0]["min"], expected["parameters"][0]["min"])


def test_bad_data_instantaneous_single_parameter1():
   
    data = np.array([5.0, 10.0, np.nan, np.nan, 5.5])
    
    expected = {
        "parameters": [{
            "code": "03_00065",
            "description": "Gage height, feet",
            "index": 4,
            "data": data,
            "mean": np.nanmean(data),
            "max": np.nanmax(data),
            "min": np.nanmin(data),
        }] 
    }  
	
    fileobj = StringIO(fixture["bad_data_instantaneous_single_parameter1"])
    actual = nwispy_filereader.read_file_in(filestream = fileobj)

    nose.tools.assert_almost_equals(actual["parameters"][0]["data"].all(), expected["parameters"][0]["data"].all())
       
    nose.tools.assert_almost_equals(actual["parameters"][0]["mean"], expected["parameters"][0]["mean"])
    nose.tools.assert_almost_equals(actual["parameters"][0]["max"], expected["parameters"][0]["max"])
    nose.tools.assert_almost_equals(actual["parameters"][0]["min"], expected["parameters"][0]["min"])

def test_bad_data_instantaneous_single_parameter2():
   
    data = np.array([np.nan, np.nan, np.nan, np.nan, 50])
    
    expected = {
        "parameters": [{
            "code": "03_00065",
            "description": "Gage height, feet",
            "index": 4,
            "data": data,
            "mean": np.nanmean(data),
            "max": np.nanmax(data),
            "min": np.nanmin(data),
        }] 
    }  
	
    fileobj = StringIO(fixture["bad_data_instantaneous_single_parameter2"])
    actual = nwispy_filereader.read_file_in(filestream = fileobj)

    nose.tools.assert_almost_equals(actual["parameters"][0]["data"].all(), expected["parameters"][0]["data"].all())
    
    nose.tools.assert_almost_equals(actual["parameters"][0]["mean"], expected["parameters"][0]["mean"])
    nose.tools.assert_almost_equals(actual["parameters"][0]["max"], expected["parameters"][0]["max"])
    nose.tools.assert_almost_equals(actual["parameters"][0]["min"], expected["parameters"][0]["min"]) 


    