"""
:Module: nwis_webservice.py

:Author: Jeremiah Lant
 
:Email: jlant@usgs.gov

:Purpose: 

Retrieve nwis data files using USGS NWIS webservices

"""

import urllib
import re

"""
user_parameters = {
    "site": "03284000",
    "format": "rdb",
    "startDt": "2014-02-12",
    "endDt": "2014-02-19"
#    "parameterCD": ",".join(["00065", "00060"])
}

base_url = "http://waterservices.usgs.gov/nwis/iv/?"

siteinfo_url = urllib.urlencode(user_parameters)

f = urllib.urlopen(base_url + siteinfo_url)

nwis_data = f.readlines()

open("test-urloutput-ivall.txt", "wb").writelines(nwis_data)
"""

"""
# read usgs-webservice-request.txt
with open("usgs-webservice-request.txt", "r") as f:    
    data_file = f.readlines()
    
    patterns = {
        'column_names': '(#)(.+)', 
        'data_row': '(dv|iv|site)(.+)'
    }       
    
    for line in data_file: 
        match_column_names = re.search(pattern = patterns['column_names'], string = line)
        match_data_row = re.search(pattern = patterns['data_row'], string = line)    
        
        if match_column_names:        
            print(match_column_names.group(2).strip().split("\t"))
            
        if match_data_row:        
            print(match_data_row.group(0).strip().split("\t"))
"""            
def main():
    """ Test functionality of webservice """


if __name__ == "__main__":
    main()