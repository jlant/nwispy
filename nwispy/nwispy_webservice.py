# -*- coding: utf-8 -*-
"""
:Module: nwispy_webservice.py

:Author: Jeremiah Lant, jlant@usgs.gov, U.S. Geological Survey, Kentucky Water Science Center, http://www.usgs.gov/ 

:Synopsis: Handles webservices for U.S. Geological Survey (USGS) National Water Information System (NWIS) data files; http://waterdata.usgs.gov/nwis ; http://waterservices.usgs.gov/nwis/
"""

__author__   = "Jeremiah Lant, jlant@usgs.gov, U.S. Geological Survey, Kentucky Water Science Center."
__copyright__ = "http://www.usgs.gov/visual-id/credit_usgs.html#copyright"
__license__   = __copyright__
__contact__   = __author__

import os
import re
import urllib
import urllib2
from StringIO import StringIO

def read_webrequest(filepath):
    """    
    Open web request file, create a file object for read_webrequest_in(filestream) 
    to process.    
    
    Parameters
    ----------
    filepath : str
        String file path.
    
    Returns
    -------
    data : dictionary
        A dictionary holding data found in file. 

    See Also
    --------
    read_webrequest_in : Read data file object         
    """    
    with open(filepath, "r") as f:
        data = read_webrequest_in(f)
        
    return data

def read_webrequest_in(filestream):
    """    
    Read a webrequest file and put data into a dictionary.
   
    Parameters
    ----------
    filestream : file object
        A file object that contains an open data file.
    
    Returns
    -------
    data : dictionary
        A dictionary holding data found in file. 

    Notes
    -----
    data = {"column names": [], "requests": []}
               
    The "requests" key in the data dictionary contains a list of dictionaries containing
    the requests information found in the requests file. For example:
    
    requests[0] = {"data type": str, "site number": str, "start date": str, "end date": str, "parameters": list of str}       
    """
    data_file = filestream.readlines()

    patterns = {
        "column_names": "(#)(.+)", 
        "dv_iv_row": "(dv|iv|)\t([0-9]+)\t([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})\t([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})\t(.+)", # match site only at the beginning of a line
        "site_row": "(site)\t([0-9]+)" 
    }  

    # initialize a dictionary to hold all the data 
    data = {
        "column names": [],
        "requests": [],
    } 

    for line in data_file: 
        match_column_names = re.search(pattern = patterns["column_names"], string = line)
        match_dv_iv_row = re.search(pattern = patterns["dv_iv_row"], string = line)
        match_site_row = re.search(pattern = patterns["site_row"], string = line)  
        
        if match_column_names:
            data["column names"] = match_column_names.group(2).strip().split("\t")
            
        if match_dv_iv_row:
            data["requests"].append({
                "data type": match_dv_iv_row.group(1),
                "site number": match_dv_iv_row.group(2),
                "start date": match_dv_iv_row.group(3),
                "end date": match_dv_iv_row.group(4),
                "parameters": match_dv_iv_row.group(5).strip().split("\t")                
            })

        if match_site_row:
            data["requests"].append({
                "data type": match_site_row.group(1),
                "site number": match_site_row.group(2),
                "start date": "",
                "end date": "",
                "parameters": ""                
            })

    return data

def encode_url(data_request):
    """    
    Encode the url needed for the USGS NWIS webservice based on users requests.
    
    Parameters
    ----------
    data_request : dictionary
        A dictionary containing data requests.
    
    Returns
    -------
    request_url : str
        String encoded url.
        
    Examples
    --------
    >>> import nwispy_webservice
    >>> request = {"data type": "dv", "site number": "03284000", "start date": "2014-01-01", "end date": "2014-01-15", "parameters": ["00060"]}
    >>> nwispy_webservice.encode_url(data_request = request)
    'parameterCD=00060&endDt=2014-01-15&startDt=2014-01-01&site=03284000&format=rdb'
    """
  
    user_parameters = {
        "format": "rdb",
        "site": data_request["site number"],
        "startDt": data_request["start date"],
        "endDt": data_request["end date"],
        "parameterCD": ",".join(data_request["parameters"])
    }
    
    user_parameters_url = urllib.urlencode(user_parameters)
    
    return user_parameters_url
    
def download_file(user_parameters_url, data_type, filename, file_destination):
    """    
    Download data from the web and save files to a specified file destination 
    with a specified filename.

    Parameters
    ----------
    user_parameters_url : str
        String encoded url based on user request file.
    data_type : str
        String of intantaneous data (iv) or daily data (dv).
    filename : str
        String filename.
    file_destination : str
        String path to save file to.
    
    Notes
    -----    
    The base url for USGS NWIS Webservice - http://waterservices.usgs.gov/nwis/
    """    
    base_url = "http://waterservices.usgs.gov/nwis/" + data_type + "/?"    

    request = urllib2.Request(base_url, user_parameters_url)
    response = urllib2.urlopen(request)  

    outputfile = os.path.join(file_destination, filename)        
    with open(outputfile, "wb") as f:
        f.write(response.read())        
        
def test_read_webrequest_in():
    """ Test functionality of read_webrequest_in"""
    
    print("--- Testing read_webrequest_in() ---")    
    
    fixture = {}
    fixture["data file"] = \
    """    
        # data_type	site_num	start_date	end_date	parameters
        dv	03284000	2014-01-01	2014-03-10	00060	00065  
        iv	03375000	2014-02-12	2014-02-19	00010	00045	00060  
    """       

    fileobj = StringIO(fixture["data file"])
    
    data = read_webrequest_in(fileobj)

    print("Number of requests expected : actual")
    print("    2 : {}".format(len(data["requests"])))
    print("")
    
    print("*Data type* expected : actual")
    print("    dv : {}".format(data["requests"][0]["data type"]))
    print("    iv : {}".format(data["requests"][1]["data type"]))
    print("")
    print("*Site number* expected : actual")
    print("    03284000 : {}".format(data["requests"][0]["site number"]))
    print("    03375000 : {}".format(data["requests"][1]["site number"]))       
    print("")
    print("*Start date* expected : actual")
    print("    2014-01-01 : {}".format(data["requests"][0]["start date"]))
    print("    2014-02-12 : {}".format(data["requests"][1]["start date"]))       
    print("")    
    print("*End date* expected : actual")
    print("    2014-03-10 : {}".format(data["requests"][0]["end date"]))
    print("    2014-02-19 : {}".format(data["requests"][1]["end date"]))       
    print("") 
    print("*Parameters* expected : actual")
    print("    [00060, 00065] : {}".format(data["requests"][0]["parameters"]))
    print("    [00060, 00065, 00045] : {}".format(data["requests"][1]["parameters"]))       
    print("") 
    
def test_encode_url():
    """ Test functionality of encode_url """
    
    print("--- Testing encode_url() ---")  
        
    data_requests = [
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

    request_url = []    
    for request in data_requests:    
        request_url.append(encode_url(request))

    print("*Encoded url 1* expected : actual")
    print("    parameterCD=00060&endDt=2014-01-15&startDt=2014-01-01&site=03284000&format=rdb : \n    {}".format(request_url[0]))
    print("")
    print("    parameterCD=00060%2C00065&endDt=2014-01-15&startDt=2014-01-01&site=03284000&format=rdb : \n    {}".format(request_url[1]))
    print("")
    print("*Encoded url 2* expected : actual")
    print("    parameterCD=00060%2C00065%2C00045&endDt=2014-02-19&startDt=2014-02-12&site=03284000&format=rdb : \n    {}".format(request_url[2]))
    print("")
    print("    parameterCD=&endDt=&startDt=&site=&format=rdb : \n    {}".format(request_url[3]))
    print("")
           
def main():
    """ Test nwispy_webservice """
    
    test_read_webrequest_in()

    test_encode_url()
    
if __name__ == "__main__":
    main()