# -*- coding: utf-8 -*-
"""
:Module: nwispy_filereader.py

:Author: Jeremiah Lant, jlant@usgs.gov, U.S. Geological Survey, Kentucky Water Science Center, http://www.usgs.gov/  

:Synopsis: Handles reading, processing, and logging errors in U.S. Geological Survey (USGS) National Water Information System (NWIS) data files; http://waterdata.usgs.gov/nwis.
"""

__author__   = "Jeremiah Lant, jlant@usgs.gov, U.S. Geological Survey, Kentucky Water Science Center."
__copyright__ = "http://www.usgs.gov/visual-id/credit_usgs.html#copyright"
__license__   = __copyright__
__contact__   = __author__

import re
import numpy as np
import datetime
import logging
from StringIO import StringIO

# my modules
import nwispy_helpers

def read_file(filepath):
    """    
    Open NWIS file, create a file object for read_file_in(filestream) to process.
    This function is responsible to opening the file, removing the file opening  
    responsibility from read_file_in(filestream) so that read_file_in(filestream)  
    can be unit tested.
    
    Parameters
    ----------
    filestream : file object        
        A file object that contains an open data file.
        
        
    Returns
    -------
    data : dictionary     
        Returns a dictionary containing data found in data file. 


    See Also
    --------
    read_file_in : Read data file object           
    """    
    with open(filepath, "r") as f:
        data = read_file_in(f)
        
    return data

def read_file_in(filestream):
    """    
    Read and process an USGS NWIS data file. Find all parameters and their respective data. 
    Missing data values are replaced with a NAN value. A dictionary is returned
    containing relevant data found in the data file.
    
    Parameters
    ----------
    filestream : file object
        A python file object that contains an open data file.
        
    Returns
    -------
    data : dictionary 
        Returns a dictionary containing data found in data file. 

    Notes
    -----
    data = {
    
        "date_retrieved": None,
        
        "gage_name": None,
        
        "column_names": None,
        
        "parameters": [],
        
        "dates": [],
        
        "timestep": None   
    }      
            
    The "parameters" key in the data dictionary contains a list of dictionaries containing
    the parameters found in the data file. For example:
    
    parameters[0] = {
    
        "code": string of NWIS code,
        
        "description": string of NWIS description,
        
        "index": integer of column index data is located,
        
        "data": numpy array of data values,
        
        "mean": mean of data values,
        
        "max": max of data values,
        
        "min": min of data values
    }         
    """  
    data_file = filestream.readlines()

    # regular expression patterns in data file 
    # column_names and data_row patterns have 5 groups which is used to 
    # distinguish a daily file from an instanteous file; if 4th group is None, 
    # then data file is daily, otherwise it is an instantaneous file.
    patterns = {
        "date_retrieved": "(.+): ([0-9]{4}-[0-9]{2}-[0-9]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2})(.+)",  
        "gage_name": "(#.+)(USGS [0-9]+\s.+)",
        "parameters": "(#)\D+([0-9]{2})\D+([0-9]{5})(\D+[0-9]{5})?(.+)",
        "column_names": "(agency_cd)\t(site_no)\t(datetime)\t(tz_cd)?(.+)",
        "data_row": "(USGS)\t([0-9]+)\t([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})\s?([0-9]{2}:[0-9]{2}\t[A-Z]{3})?(.+)"
    }    
    
    # initialize a dictionary to hold all the data of interest
    data = {
        "date_retrieved": None,
        "gage_name": None,
        "column_names": None,
        "parameters": [],
        "dates": [],
        "timestep": None
    }      
    
    # process file; find matches and add to data dictionary
    for line in data_file: 
        match_date_retrieved = re.search(pattern = patterns["date_retrieved"], string = line)
        match_gage_name = re.search(pattern = patterns["gage_name"], string = line)
        match_parameters = re.search(pattern = patterns["parameters"], string = line)
        match_column_names = re.search(pattern = patterns["column_names"], string = line)
        match_data_row = re.search(pattern = patterns["data_row"], string = line)
     
        # if match is found add it to data dictionary; date is in second group of the match
        if match_date_retrieved:
            data["date_retrieved"] = match_date_retrieved.group(2)
        
        # get the gage name which is the second group in the pattern
        if match_gage_name:
            data["gage_name"] = match_gage_name.group(2)
        
        # get the parameters available in the file and create a dictionary for each parameter
        if match_parameters:
            code, description = get_parameter_code(match = match_parameters)  
            
            data["parameters"].append({ 
                "code": code, 
                "description": description,
                "index": None,
                "data": [],
                "mean": None,
                "max": None,
                "min": None
            })
            
        # get the column names and indices of existing parameter(s) 
        if match_column_names:
            data["column_names"] = match_column_names.group(0).split("\t")

            for parameter in data["parameters"]:
                parameter["index"] = data["column_names"].index(parameter["code"])           

         # get date and float value
        if match_data_row:
            date = get_date(daily = match_data_row.group(3), instantaneous = match_data_row.group(4))
            data["dates"].append(date)
            
            for parameter in data["parameters"]:
                value = match_data_row.group(0).split("\t")[parameter["index"]]
                
                value = convert_to_float(value = value, helper_str = "parameter {} on {}".format(parameter["code"], date.strftime("%Y-%m-%d_%H.%M")))
                                       
                parameter["data"].append(value)
    
    # convert the date list to a numpy array
    data["dates"] = np.array(data["dates"])    

    # find timestep 
    timestep = data["dates"][1] - data["dates"][0]
    if timestep.days == 1:
        data["timestep"] = "daily"
    else:
        data["timestep"] = "instantaneous"
    
    # convert each parameter data list in data["parameter"] to a numpy array and
    # compute mean, max, and min
    for parameter in data["parameters"]:
        parameter["data"] = np.array(parameter["data"])
        
        param_mean, param_max, param_min = compute_simple_stats(data = parameter["data"])
        
        parameter["mean"] = param_mean
        parameter["max"] = param_max
        parameter["min"] = param_min

    return data

def compute_simple_stats(data):
    """   
    Compute simple statistics (mean, max, min) on a data array. Can handle nan values.
    If the entire data array consists of only nan values, then log the error and raise a ValueError.
    
    Parameters
    ----------
    data : array
        An array of numbers to compute simple statistics on. 
        
    Returns
    -------
    (mean, max, min) : tuple 
        Returns a tuple of mean, max, and min stats.        

    Raises
    ------
    ValueError
        If data array only contains nan values.

    Examples
    --------
    >>> import nwispy_filereader
    >>> import numpy as np
    >>> nwispy_filereader.compute_simple_stats([1, 2, 3, 4])
    (2.5, 4, 1)
    
    >>> nwispy_filereader.compute_simple_stats([2, np.nan, 6, 1])
    (3.0, 6.0, 1.0)
    """    
    # check if all values are nan
    if not np.isnan(data).all():
        param_mean = np.nanmean(data)
        param_max = np.nanmax(data)
        param_min = np.nanmin(data)
        
        return param_mean, param_max, param_min
    else:
        error_str = "*Bad data* All values are NaN. Please check data"
        logging.warn(error_str)
        
        raise ValueError

def convert_to_float(value, helper_str = None):
    """   
    Convert a value to a float. If value is not a valid float, log as an error
    with a helper_str (i.e. value's coorsponding date) to help locate the 
    error and replace value with a nan.
    
    Parameters
    ----------
    value : str
        String value to convert.
    helper_str : str
        String message to be placed in error log if value can not be converted to a float. i.e. value's corresponding date of occurance.
        
    Returns
    -------
    value : {float, nan}
        Float or numpy nan value 
    """
    # remove any special characters present in string value except for period character
    value = nwispy_helpers.rmspecialchars(value)    
    
    if nwispy_helpers.isfloat(value):
        value = float(value)
    else:        
        if value == "":
            error_str = "*Missing value* {}. *Solution* - Replacing with NaN value".format(helper_str)
            logging.warn(error_str)
            value = np.nan

        else:
            error_str = "*Bad value* {}. *Solution* - Replacing with NaN value".format(helper_str)
            logging.warn(error_str)
            value = np.nan
            
    return value


def get_parameter_code(match):
    """   
    Get code and description strings from regular expression match object.
    
    Parameters
    ----------
    match : re object
        Regular expression match object.
        
    Returns
    -------
    (code, description) : tuple of str
        Tuple containing parameter code string and description string.
    
    Note
    ----
    string:  "#    06   00060     00003     Discharge, cubic feet per second (Mean)"
    
    match.groups(0):  ("#", "06", "00060", "00003", "     Discharge, cubic feet per second (Mean)")
    
    match.group(1) = "#"
    
    match.group(2) = "06"
    
    match.group(3) = "00060"
    
    match.group(4) = "00003"
    
    match.group(5) = "Discharge, cubic feet per second (Mean)"        
    """ 
    
    # get the proper information from each group
    dd = match.group(2)
    param = match.group(3)
    
    # concatenate dd and param using "_" as in the column names
    code = "_".join((dd, param))            
    
    # get parameter description
    description = match.group(5).strip()    
    
    # if statistic exists, then add that to the string
    if match.group(4):
        statistic =  match.group(4).strip()
        code = "_".join((code, statistic)) 
   
    return (code, description)

def get_date(daily, instantaneous):
    """   
    Parse date strings and return a datetime object.
    
    Parameter
    ---------
    daily : str
        String in a daily forma. i.e. 2013-06-25
    intantaneous : str
        String in an intantaneous format. i.e. 00:15\tEDT
    
    Returns
    -------
    date : datetime object           
    """
    # get date from the data row
    year = daily.split("-")[0]
    month = daily.split("-")[1]
    day = daily.split("-")[2]
    hour = 0
    minute = 0
    
    # if data row has a date in instantaneous format, then get hour and minute after removing the "EDT"
    if instantaneous:
        instantaneous = instantaneous.split("\t")[0]
        hour = instantaneous.split(":")[0]
        minute = instantaneous.split(":")[1]
                
    date = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
    
    return date
    
    
def test_get_parameter_code():
    """ Test the get_parameter_code functionality """
    
    print("--- Testing get_parameter_code() ---")
    
    pattern = "(#)\D+([0-9]{2})\D+([0-9]{5})(\D+[0-9]{5})?(.+)"    
    code, description = get_parameter_code(match = re.search(pattern , "#    06   00060     00003     Discharge, cubic feet per second (Mean)"))
    print("*Code* expected : actual")
    print("    06_00060_00003 : {}".format(code))
    print("*Description* expected : actual")
    print("    Discharge, cubic feet per second (Mean) : {}".format(description))

    print("")
    
    code, description = get_parameter_code(match = re.search(pattern, "#    02   00065     Gage height, feet"))
    print("*Code* expected : actual")
    print("    02_00065 : {}".format(code))
    print("*Description* expected : actual")
    print("    Gage height, feet : {}".format(description))

    print("")

def test_get_date():
    """ Test the get_date functionality """
    
    print("--- Testing get_date() ---")
    
    date1 = get_date(daily = "2014-03-12", instantaneous = "")
    print("*Date* expected : actual")
    print("    2014-03-12 : {}".format(date1))

    date2 = get_date(daily = "2014-03-12", instantaneous = "01:15\tEDT")
    print("Date expected : actual")
    print("    2014-03-12 at 01:15:00 : {}".format(date2))  
    
    print("")    

def test_read_file_in():
    """ Test read_file_in() functionality"""

    print("--- Testing read_file_in() ---")

    fixture = {}
    
    fixture["data file"] = \
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

    fileobj = StringIO(fixture["data file"])
    
    data = read_file_in(fileobj)   
    print("*Date retrieved* expected : actual")
    print("    2014-03-11 08:40:40 : {}".format(data["date_retrieved"]))
    print("")
    print("*Gage name* expected : actual")
    print("    USGS 03401385 DAVIS BRANCH AT HIGHWAY 988 NEAR MIDDLESBORO, KY : {}".format(data["gage_name"]))
    print("")
    print("*Column names* expected : actual")
    print("    [agency_cd, site_no, datetime, tz_cd, 02_00065, 02_00065_cd, 03_00010, 03_00010_cd, 04_00300, 04_00300_cd, 05_00400, 05_00400_cd, 06_00095, 06_00095_cd, 07_63680, 07_63680_cd] : \n{}".format(data["column_names"]))
    print("")
    print("*Timestep* expected : actual")
    print("    instantaneous : {}".format(data["timestep"]))
    print("")
    print("*Dates* type expected : actual")
    print("    numpy.ndarray : {}".format(type(data["dates"]))) 
    print("")   
    print("*Dates* expected : actual")
    print("    [datetime.datetime(2013, 6, 6, 0, 0) datetime.datetime(2013, 6, 6, 0, 15) datetime.datetime(2013, 6, 6, 0, 30)] datetime.datetime(2013, 6, 6, 0, 45) datetime.datetime(2013, 6, 6, 1, 0)] : \n{}".format(data["dates"]))
    print("")
    print("Data type expected : actual")
    print("    numpy.ndarray : {}".format(type(data["parameters"][0]["data"])))    
    print("")
    print("*Parameters* expected index, code, description, data, mean, max, min")
    print("    4 02_00065 Gage height, feet [1.0 2.0 3.0 4.0 5.0]  3.0 5.0 1.0\n")
    print("    6 03_00010 Temperature, water, degrees Celsius [5.0 10.0 15.0 20.0 25.0]  15.0 25.0 5.0\n")   
    print("    8 04_00300 Dissolved oxygen, water, unfiltered, milligrams per liter [2.0 1.25 1.25 0.25 0.25]  1.0 2.0 0.25\n")
    print("    10 05_00400 pH, water, unfiltered, field, standard units [-4.0 4.0 3.5 3.5 3.0]  2.0 4.0 -4.0\n")
    print("    12 06_00095 Specific conductance, water, unfiltered, microsiemens per centimeter at 25 degrees Celsius [2.0 1.0 0.0 -1.0 -2.0]  0.0 2.0 -2.0\n")      
    print("    14 07_63680 Turbidity, water, unfiltered, monochrome near infra-red LED light, 780-900 nm, detection angle 90 +-2.5 degrees, formazin nephelometric units (FNU) [8.25 8.25 3.5 2.5 2.5]  5.0 8.25 2.5\n")    
    
    print("*Parameters* ACTUAL index, code, description, data, mean, max, min")
    for parameter in data["parameters"]:
        print("    {} {} {} {} {} {} {}".format(parameter["index"], parameter["code"], parameter["description"], parameter["data"], parameter["mean"], parameter["max"], parameter["min"]))    

    print("")

def main():
    """ Test functionality of reading files """
    
    test_get_parameter_code()
    
    test_get_date()
    
    test_read_file_in()
    
if __name__ == "__main__":
    main()