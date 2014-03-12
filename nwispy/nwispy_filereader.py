"""
:Module: nwispy_filereader.py

:Author: Jeremiah Lant
 
:Email: jlant@usgs.gov

:Purpose: 

Read USGS National Water Information System (NWIS) data files.

"""
import sys
import os
import re
import numpy as np
from scipy.stats import nanmean 
import datetime
import logging
import pdb
# my modules
import nwispy_helpers



def start_logging_errors(error_path):
    """ 
    Start error logging object
    
    *Parameters:*
        outputdir : string path
    
    *Return:*
        no return  
        
    """     
    logging.basicConfig(filename = '/'.join([error_path, "file-errors.log"]), filemode = "w", level = logging.INFO)
        
def stop_logging_errors():
    """ 
    Stop error logging object
    
    *Parameters:*
        no input parameters
    
    *Return:*
        no return  
        
    """ 
    logging.shutdown()

def read_file(filepath, error_path):
    """    
    Open NWIS file, create a file object for read_file_in(filestream) to process.
    This function is responsible to opening the file, removing the file opening  
    responsibility from read_file_in(filestream) so that read_file_in(filestream)  
    can be unit tested.
    
    *Parameters:*
		filepath : string path to NWIS file
    
    *Return:*
        data : dictionary holding data found in NWIS data file  
        
    """    
    with open(filepath, "r") as f:
        filedir, filename = nwispy_helpers.get_filedir_filename(filepath)
        start_logging_errors(error_path = error_path)

        data = read_file_in(f)
    
        stop_logging_errors()
        
    return data

def read_file_in(filestream):
    """    
    Read and process a USGS NWIS file. Finds any parameter and its respective data. 
    Relevant data is put into a dictionary (see Return section).  Missing data values
    are replaced with a NAN value.  
    
    *Parameters:*
        filestream: file object
    
    *Return:*
        data: dictionary holding data found in NWIS data file
        
        data = {
            'date_retrieved': None,
            
            'gage_name': None,
            
            'column_names': None,
            
            'parameters': [],
            
            'dates': [],
            
            'timestep': None   
        }      
                
        ** Note: The 'parameters' key contains a list of dictionaries containing
        the parameters found in the data file; i.e.
        
        parameters[0] = {
            'code': string of NWIS code,
            
            'description': string of NWIS description,
            
            'index': integer of column index data is located,
            
            'data': numpy array of data values,
            
            'mean': mean of data values,
            
            'max': max of data values,
            
            'min': min of data values
        }        
        
    """  
    data_file = filestream.readlines()
    
    # regular expression patterns in data file 
    # column_names and data_row patterns have 5 groups which is used to 
    # distinguish a daily file from an instanteous file; if 4th group is None, 
    # then data file is daily, otherwise it is an instanteous file.
    patterns = {
        'date_retrieved': '(.+): (.{4}-.{2}-.{2}) (.{2}:.{2}:.{2}) (.+)', 
        'gage_name': '(#.+)(USGS.+)',
        'parameters': '(#)\D+([0-9]{2})\D+([0-9]{5})(\D+[0-9]{5})?(.+)',
        'column_names': '(agency_cd)\t(site_no)\t(datetime)\t(tz_cd)?(.+)',
        'data_row': '(USGS)\t([0-9]+)\t([0-9]{4}-[0-9]{1,2}-[0-9]{1,2})\s?([0-9]{2}:[0-9]{2}\t[A-Z]{3})?(.+)'
    }    
    
    # initialize a dictionary to hold all the data of interest
    data = {
        'date_retrieved': None,
        'gage_name': None,
        'column_names': None,
        'parameters': [],
        'dates': [],
        'timestep': None
    }      
    
    # process file; find matches and add to data dictionary
    for line in data_file: 
        match_date_retrieved = re.search(pattern = patterns['date_retrieved'], string = line)
        match_gage_name = re.search(pattern = patterns['gage_name'], string = line)
        match_parameters = re.search(pattern = patterns['parameters'], string = line)
        match_column_names = re.search(pattern = patterns['column_names'], string = line)
        match_data_row = re.search(pattern = patterns['data_row'], string = line)
     
        # if match is found add it to data dictionary; date is in second group of the match
        if match_date_retrieved:
            data['date_retrieved'] = match_date_retrieved.group(2)
        
        # get the gage name which is the second group in the pattern
        if match_gage_name:
            data['gage_name'] = match_gage_name.group(2)
        
        # get the parameters available in the file and create a dictionary for each parameter
        if match_parameters:
            code, description = get_parameter_code(match = match_parameters)  
            
            data['parameters'].append({ 
                'code': code, 
                'description': description,
                'index': None,
                'data': [],
                'mean': None,
                'max': None,
                'min': None
            })
            
        # get the column names and indices of existing parameter(s) 
        if match_column_names:
            data['column_names'] = match_column_names.group(0).split('\t')

            for parameter in data['parameters']:
                parameter['index'] = data['column_names'].index(parameter['code'])           

         # get date; match_data_row.group(3) => daily match, match_data_row.group(4) => instantaneous match
        if match_data_row:
            date = get_date(daily = match_data_row.group(3), instantaneous = match_data_row.group(4))
            data['dates'].append(date)
            
            for parameter in data['parameters']:
                value = match_data_row.group(0).split('\t')[parameter['index']]
                
                if not nwispy_helpers.is_float(value):
                    if value == "":
                        error_str = '**Missing value on ' + str(date) + ' *Filling with Not A Number (NAN)'
                        print(error_str)
                        logging.info(error_str)
                        value = np.nan
                    
                    elif '_' in value:
                        error_str = '**Bad value with float on ' + str(date) + ' *Splitting on _ character'
                        print(error_str)
                        logging.info(error_str)
                        value = value.split('_')[0]
                    
                    else:
                        error_str = '**ERROR on ' + str(date) +' Value can not be converted to a float: ' + value + '**Exiting. Bad data in file!'
                        raise ValueError(error_str)
                        sys.exit('**Exiting. Bad data in file!')
                        
                parameter['data'].append(float(value))    
    
    # convert the date list to a numpy array
    data['dates'] = np.array(data['dates'])    

    # find timestep of the data
    timestep = data['dates'][1] - data['dates'][0]
    if timestep.days == 1:
        data['timestep'] = 'daily'
    else:
        data['timestep'] = 'instantaneous'
    
    # convert each parameter data list in data['parameter'] convert to a numpy array and
    # compute mean, max, and min as well.
    for parameter in data['parameters']:
        parameter['data'] = np.array(parameter['data'])       
        parameter['mean'] = nanmean(parameter['data'])
        parameter['max'] = np.nanmax(parameter['data'])
        parameter['min'] = np.nanmin(parameter['data'])
        
    return data

def get_parameter_code(match):
    """   
    Get code and description from existing parameters.
    
    *Parameters*:
        match: regular expression match object
        
    *Return*:
        (code, description): tuple of code and description
    
    *Example*:
        string:  '#    06   00060     00003     Discharge, cubic feet per second (Mean)'
        
        match.groups(0):  ('#', '06', '00060', '00003', '     Discharge, cubic feet per second (Mean)')
        
        match.group(1) = '#'
        
        match.group(2) = '06'
        
        match.group(3) = '00060'
        
        match.group(4) = '00003'
        
        match.group(5) = 'Discharge, cubic feet per second (Mean)'
        
    """ 
    
    # get the proper information from each group
    dd = match.group(2)
    param = match.group(3)
    
    # concatenate dd and param using '_' as in the column names
    code = '_'.join((dd, param))            
    
    # get parameter description
    description = match.group(5).strip()    
    
    # if statistic exists, then add that to the string
    if match.group(4):
        statistic =  match.group(4).strip()
        code = '_'.join((code, statistic)) 
   
    return (code, description)

def get_date(daily, instantaneous):
    """   
    Parse the date strings from a data row.
    
    *Parameters*:
        daily: string of daily format; i.e. 2013-06-25
        
        intantaneous: string of intantaneous format; i.e. 00:15\tEDT
    
    *Return*:
        date: datetime object   
        
    """
    # get date from the data row
    year = daily.split('-')[0]
    month = daily.split('-')[1]
    day = daily.split('-')[2]
    hour = 0
    minute = 0
    
    # if data row has a date in instantaneous format, then get hour and minute after removing the 'EDT'
    if instantaneous:
        instantaneous = instantaneous.split('\t')[0]
        hour = instantaneous.split(':')[0]
        minute = instantaneous.split(':')[1]
                
    date = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
    
    return date


def test_get_parameter_code():
    """ test the get parameter code function """
    print("**Testing get_parameter_code() **")
    print("")
    
    pattern = "(#)\D+([0-9]{2})\D+([0-9]{5})(\D+[0-9]{5})?(.+)"    
    code, description = get_parameter_code(match = re.search(pattern , "#    06   00060     00003     Discharge, cubic feet per second (Mean)"))
    print("code: {}".format(code))
    print("description: {}".format(description))

    print("")
    
    code, description = get_parameter_code(match = re.search(pattern, "#    02   00065     Gage height, feet"))
    print("code: {}".format(code))
    print("description: {}".format(description))


def test_get_date():
    """ test the get date function """
    print("**Testing get_date()**")
    print("")
    
    date1 = get_date(daily = "2014-03-12", instantaneous = "")
    print(date1)

    date2 = get_date(daily = "2014-03-12", instantaneous = "01:15\tEDT")
    print(date2)  
    
    print("")    

def main():
    """ Test functionality of reading files """
    test_get_date()
    
    test_get_parameter_code()

if __name__ == "__main__":
    main()