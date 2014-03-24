"""
:Module: nwispy_webservice.py

:Author: Jeremiah Lant
 
:Email: jlant@usgs.gov

:Purpose: 

Retrieve nwis data files using USGS NWIS webservices

"""

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
        **filepath** : string path to file
    
    Return
    ------
        **data** : dictionary holding data found in file  
        
    """    
    with open(filepath, "r") as f:
        data = read_webrequest_in(f)
        
    return data

def read_webrequest_in(filestream):
    """    
    Read a webrequest file and put data into a dictionary
    
    Parameters
    ----------
        **filestream** : file object
    
    Return
    ------
        **data** : dictionary holding data found in file
    """
    data_file = filestream.readlines()

    patterns = {
        'column_names': '(#)(.+)', 
        'dv_iv_row': '(dv|iv|)\t([0-9]+)\t([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})\t([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})\t(.+)', # match site only at the beginning of a line
        'site_row': '(site)\t([0-9]+)' 
    }  

    # initialize a dictionary to hold all the data 
    data = {
        "column names": [],
        "requests": [],
    } 

    for line in data_file: 
        match_column_names = re.search(pattern = patterns['column_names'], string = line)
        match_dv_iv_row = re.search(pattern = patterns['dv_iv_row'], string = line)
        match_site_row = re.search(pattern = patterns['site_row'], string = line)  
        
        if match_column_names:
            data['column names'] = match_column_names.group(2).strip().split("\t")
            
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
        **data_request** : dictionary containing a data request
    
    Return
    ------
        **request_url** : string encoded url
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
    Get data from the web and save files with provided filename to local machine.
    
    The base url for USGS NWIS Webservice is:
        base_url = "http://waterservices.usgs.gov/nwis/
    
    Parameters
    ----------
        **user_parameters_url** : encoded url based on users request
        **data_type** : string "iv" or "dv"
        **filename** : string
        **file_destination** : string path 
    
    Return
    ------
        **no return**  
    """    
    base_url = "http://waterservices.usgs.gov/nwis/" + data_type + "/?"    

    request = urllib2.Request(base_url, user_parameters_url)
    response = urllib2.urlopen(request)  

    outputfile = os.path.join(file_destination, filename)        
    with open(outputfile, 'wb') as f:
        f.write(response.read())        
        
def test_read_webrequest_in():
    """ Test functionality of read_webrequest_in"""
    
    print("** Testing read_webrequest_in() **")    
    
    fixture = {}
    fixture["data file"] = \
    """    
        # data_type	site_num	start_date	end_date	parameters
        dv	03284000	2014-01-01	2014-03-10	00060	00065  
        iv	03284000	2014-02-12	2014-02-19	00060	00065	00045  
    """       

    fileobj = StringIO(fixture["data file"])
    
    data = read_webrequest_in(fileobj)    
    print(data["requests"])
    
    print("")

def test_encode_url():
    """ Test functionality of encode_url """
    
    print("** Testing encode_url() **")  
        
    data_requests = [
        {'end date': '2014-01-15', 
        'data type': 'dv', 
        'start date': '2014-01-01', 
        'parameters': ['00060', '00065'], 
        'site number': '03284000'
        }, 
        {'end date': '2014-02-19', 
        'data type': 'iv', 
        'start date': '2014-02-12', 
        'parameters': ['00060', '00065', '00045'], 
        'site number': '03284000'
        }
    ]
    
    for request in data_requests:    
        request_url = encode_url(request)
        print(request_url)

    print("")
           
def main():
    """ Test nwispy_webservice """
    
    test_read_webrequest_in()

    test_encode_url()
    
if __name__ == "__main__":
    main()