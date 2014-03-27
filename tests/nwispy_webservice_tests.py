import nose.tools
from nose import with_setup

import sys
import numpy as np
import datetime
from StringIO import StringIO

# my module
from nwispy import nwispy_webservice



# define the global fixture to hold the data that goes into the functions you test
fixture = {}

def setup():
    """ Setup fixture for testing """

    print >> sys.stderr, "SETUP: nwispy_webservice tests"

    fixture["data file"] = \
    """    
        # data_type	site_num	start_date	end_date	parameters
        dv	03284000	2014-01-01	2014-03-10	00060	00065  
        iv	03375000	2014-02-12	2014-02-19	00010	00045	00060  
    """   

    fixture["data requests"] = [
        {"end date": "2014-01-15", 
        "data type": "dv", 
        "start date": "2014-01-01", 
        "parameters": ["00060"], 
        "site number": "03284000"
        }, 
        {"end date": "2014-01-15", 
        "data type": "dv", 
        "start date": "2014-01-01", 
        "parameters": ["00060", "00065"], 
        "site number": "03284000"
        }, 
        {"end date": "2014-02-19", 
        "data type": "iv", 
        "start date": "2014-02-12", 
        "parameters": ["00060", "00065", "00045"], 
        "site number": "03284000"
        },
        {"data type": "",
        "site number": "",
        "start date": "",
        "end date": "",
        "parameters": "", 
        }
    ]

def teardown():
    """ Print to standard error when all tests are finished """
    
    print >> sys.stderr, "TEARDOWN: nwispy_webservice tests" 


def test_read_webrequest_in():  

    expected1 = {"data type": "dv",
                "site number": "03284000",
                "start date": "2014-01-01",
                "end date": "2014-03-10",
                "parameters": ["00060", "00065"]
    }
    
    expected2  = {"data type": "iv",
                  "site number": "03375000",
                  "start date": "2014-02-12",
                  "end date": "2014-02-19",
                  "parameters": ["00010", "00045", "00060"]
    } 
    
    fileobj = StringIO(fixture["data file"])
    
    data = nwispy_webservice.read_webrequest_in(fileobj)              

    nose.tools.assert_equals(len(data["requests"]), 2)
    nose.tools.assert_equals(data["requests"][0]["data type"], expected1["data type"])
    nose.tools.assert_equals(data["requests"][0]["site number"], expected1["site number"])    
    nose.tools.assert_equals(data["requests"][0]["start date"], expected1["start date"])  
    nose.tools.assert_equals(data["requests"][0]["end date"], expected1["end date"])  
    nose.tools.assert_equals(data["requests"][0]["parameters"], expected1["parameters"])  

    
    nose.tools.assert_equals(data["requests"][1]["data type"], expected2["data type"])
    nose.tools.assert_equals(data["requests"][1]["site number"], expected2["site number"]) 
    nose.tools.assert_equals(data["requests"][1]["start date"], expected2["start date"])  
    nose.tools.assert_equals(data["requests"][1]["end date"], expected2["end date"])  
    nose.tools.assert_equals(data["requests"][1]["parameters"], expected2["parameters"]) 

def test_endcode_url():

    expected_url = ["parameterCD=00060&endDt=2014-01-15&startDt=2014-01-01&site=03284000&format=rdb",
                    "parameterCD=00060%2C00065&endDt=2014-01-15&startDt=2014-01-01&site=03284000&format=rdb",
                    "parameterCD=00060%2C00065%2C00045&endDt=2014-02-19&startDt=2014-02-12&site=03284000&format=rdb",
                    "parameterCD=&endDt=&startDt=&site=&format=rdb"]
    
    actual_url = []
    for request in fixture["data requests"]:
        actual_url.append(nwispy_webservice.encode_url(request))

    nose.tools.assert_equals(actual_url[0], expected_url[0])
    nose.tools.assert_equals(actual_url[1], expected_url[1])
    nose.tools.assert_equals(actual_url[2], expected_url[2])
    nose.tools.assert_equals(actual_url[3], expected_url[3])
