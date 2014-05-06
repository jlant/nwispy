# -*- coding: utf-8 -*-
"""
:Module: nwispy_helpers.py

:Author: Jeremiah Lant, jlant@usgs.gov, U.S. Geological Survey, Kentucky Water Science Center, http://www.usgs.gov/ 

:Synopsis: Collection of helper functions.
"""

__author__   = "Jeremiah Lant, jlant@usgs.gov, U.S. Geological Survey, Kentucky Water Science Center."
__copyright__ = "http://www.usgs.gov/visual-id/credit_usgs.html#copyright"
__license__   = __copyright__
__contact__   = __author__

import os
import numpy as np
import datetime
import re
import logging

def now():
    """    
    Return current date and time in a format that can be used as a file name. 
    Format: year-month-day_hour.minute.second.microsecond; e.g. 2014-03-18_15.51.46.25
      
    Returns
    -------
    date_time : string
        String of current date and time in %Y-%m-%d_%H.%M.%S.%f format.       
        
    Notes
    -----
    The length of the microsecond string is trimed to 2 digits.
    """  
    date_time = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f")[:-4]
    
    return date_time

def get_file_paths(directory, file_ext = None):
    """    
    Return a list of full file paths from a directory including its subdirectories.
    Filter fil    
    
    Parameters
    ----------    
    directory : string
        String path 
    file_ext : string
        String file extention; e.g. ".txt" 
    Returns
    -------
    file_paths : list 
        List of strings of full file paths from a directory.
    """     
    file_paths = []  

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            if file_ext and filepath.endswith(file_ext):
                file_paths.append(filepath) 

    return file_paths

def get_file_info(path):
    """    
    Get file directory and name from a file path.
    
    Parameters
    ----------
    path : string
        String path
      
    Returns
    -------
    filedir : string
        String file directory path
    filename : string
        String file name    
    """ 
    filedir, filename = os.path.split(path)
    
    # filedir is an empty string when file is in current directory 
    if not filedir: 
        filedir = os.getcwd()

    return filedir, filename

def make_directory(path, directory_name):
    """    
    Make a directory if is does not exist.
    
    Parameters
    ----------
    path: string
        String path 
    directory_name : string
        String name
      
    Returns
    -------
    directory_path : string
        String path to made directory.  
    """    
    directory_path = os.path.join(path, directory_name)
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)         
    
    return directory_path

def isfloat(value):
    """   
    Determine if string value can be converted to a float. Return True if
    value can be converted to a float and False otherwise.
    
    Parameters
    ----------
    value : string
        String value to try to convert to a float.
        
    Returns
    -------
    bool : bool
        
    Examples
    --------
    >>> import nwispy_helpers
    >>> nwispy_helpers.isfloat(value = "2.5")
    True
    >>> nwispy_helpers.isfloat(value = "hello world")
    False
    >>> nwispy_helpers.isfloat(value = "5.5_")
    False
    """
    
    try:
        float(value)
        return True
        
    except ValueError:
        return False

def rmspecialchars(value):
    """   
    Remove any special characters except period (.) and negative (-) from numeric values
    
    Parameters
    ----------
    value : string
        String value to remove any existing characters from
        
    Returns
    -------
    value : string
        String value to without any special characters
        
    Examples
    --------
    >>> import helpers
    >>> helpers.rmspecialchars(value = "*6.5_")
    6.5
    >>> helpers.rmspecialchars(value = "ICE")
    ICE
    >>> helpers.rmspecialchars(value = "-4.2")
    -4.2
    >>> helpers.rmspecialchars(value = "")
    
    >>> helpers.rmspecialchars(value = "%&!@#8.32&#*;")
    8.32
    """
    value = re.sub("[^A-Za-z0-9.-]+", "", value)
    
    return value

def convert_to_float(value, helper_str = None):
    """   
    Convert a value to a float. If value is not a valid float, log as an error
    with a helper_str (e.g. value"s coorsponding date) to help locate the 
    error and replace value with a nan.
    
    Parameters
    ----------
    value : string
        String value to convert.
    helper_str : string
        String message to be placed in error log if value can not be converted to a float. e.g. value"s corresponding date of occurance.
        
    Returns
    -------
    value : {float, nan}
        Float or numpy nan value 
    """
    # remove any special characters present in string value
    value = rmspecialchars(value)    
    
    if isfloat(value):
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

def create_monthly_dict():
    """
    Create a dictionary containing monthly keys and empty lists as initial values
    
    Returns
    -------
    values_dict : dictionary
        Dictionary containing monthly keys with corresponding values.
    
    Notes
    -----
    {"January": [],
     "February": [],
     "March": [],
     "April": [],
     "May": [],
     "June": [],
     "July": [],
     "August": [],
     "September": [],
     "October": [],
     "November": [],
     "December": []
    }
    """
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]       

    # initialize dictionary
    monthly_dict = {}
    for month in months:
        monthly_dict[month] = []

    return monthly_dict

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
    >>> import watertxt
    >>> import numpy as np
    >>> watertxt.compute_simple_stats([1, 2, 3, 4])
    (2.5, 4, 1)
    
    >>> watertxt.compute_simple_stats([2, np.nan, 6, 1])
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

    
def subset_data(dates, values, start_date, end_date):
    """   
    Subset the dates and values arrays to match the range of the start_date
    and end_date. If start_date and end_date are not within the range of dates
    specified in dates, then the start_date and end_date are set to the
    first and last dates in the array dates.
            
    Parameters 
    ----------
    dates : array 
        Array of dates as datetime objects. 
    data : array
        Array of numbers.
    start_date : datetime object
        A date as a datetime object.
    end_date : datetime object
        A date as a datetime object.
        
    Returns
    -------
    (subset_dates, subset_values) : tuple 
        Tuple of arrays of dates and values that were subsetted.
    """ 
    if len(dates) != len(values):
        raise ValueError("Lengths of dates and values are not equal!")
        
    else:
        # if start_date or end_date are not within dates, set them to the 
        # first and last elements in dates
        if start_date < dates[0] or start_date > dates[-1]:
            start_date = dates[0]  
        
        if end_date > dates[-1] or end_date < dates[0]:
            end_date = dates[-1] 

        # find start and ending indices; have to convert idx from array to int to slice
        start_idx = int(np.where(dates == start_date)[0])
        end_idx = int(np.where(dates == end_date)[0])
        
        # subset variable and date range; 
        date_subset = dates[start_idx:end_idx + 1] 
        values_subset = values[start_idx:end_idx + 1] 
        
        return date_subset, values_subset

def find_start_end_dates(dates1, dates2):
    """  
    Find start and end dates between two different sized arrays of datetime
    objects.

    Parameters 
    ----------
    dates1 : list
        List of datetime objects.
        
    dates2 : list 
        List of datetime objects.
    
    Returns
    -------
    (start_date, end_date) : tuple 
        Tuple of datetime objects.
    """
    # make sure that dates overlap
    date1_set = set(dates1)    
    date2_set = set(dates2)
       
    if date1_set.intersection(date2_set):
        # pick later of two dates for start date; pick earlier of two dates for end date
        if dates2[0] > dates1[0]: 
            start_date = dates2[0]         
        else:
            start_date = dates1[0]
        
        if dates2[-1] > dates1[-1]: 
            end_date = dates1[-1]        
        else:
            end_date = dates2[-1]

        return start_date, end_date

    else:
       raise ValueError("No matching dates for find_start_end_dates()") 


def _print_test_info(expected, actual):
    """   
    For testing purposes, assert that all expected values and actual values match. 
    Prints assertion error when there is no match.  Prints values to user to scan
    if interested. Helps a lot for debugging. This function mirrors what is done
    in nosetests.
    
    Parameters
    ----------
    expected : dictionary  
        Dictionary holding expected data values
    actual : dictionary
        Dictionary holding expected data values
    """
    for key in actual.keys():
        np.testing.assert_equal(actual[key], expected[key], err_msg = "For key * {} *, actual value(s) * {} * do not equal expected value(s) * {} *".format(key, actual[key], expected[key]))        

        print("*{}*".format(key))                     
        print("    actual:   {}".format(actual[key]))  
        print("    expected: {}\n".format(expected[key])) 

def test_now():
    """ Test now() """

    print("--- Testing now() ---")    
    
    date_time_str = now()
    print("Right now is: ")
    print("    {}".format(date_time_str))
    print("")

def test_get_filepaths():
    """ Test get_filepaths() """
    
    print("--- Testing get_filepaths() ---")   
    
    file_paths = get_file_paths(os.getcwd(), file_ext = "py")
    
    print("File paths are:")
    print("    {}".format(file_paths))
    print("")

def test_get_file_info():
    """ Test get_file_info functionality """

    print("--- Testing get_file_info ---")  

    # expected values
    expected = {}
    expected["filedir"] = "C:\Users\jlant\jeremiah\projects\python-projects\waterapputils\waterapputils"
    expected["filename"] = "helpers.py"

    # actual values
    actual = {}    
    actual["filedir"], actual["filename"] = get_file_info(path = os.path.join(os.getcwd(), "helpers.py"))

    # print results
    _print_test_info(actual, expected)

def test_make_directory():
    """ Test make_directory() """

    print("---- Testing make_directory() ----")  

    # expected values
    expected = {"directory_path" : "C:\Users\jlant\jeremiah\projects\python-projects\waterapputils\waterapputils\Testing"}

    # actual values    
    actual = {"directory_path": make_directory(path = os.getcwd(), directory_name = "Testing")}

    # print results
    _print_test_info(actual, expected)

def test_isfloat():
    """ Test isfloat() """

    print("--- Testing isfloat() ---") 

    # expected values
    expected = {"2.5": True, "2": True, "string 2.5": True, "hello world": False, "2.5_": False}

    # actual values
    actual = {"2.5": isfloat(2.5), "2": isfloat(2), "string 2.5": isfloat("2.5"), "hello world": isfloat("hello world"), "2.5_": isfloat("2.5_")}

    # print results
    _print_test_info(actual, expected)

def test_convert_to_float():
    """ Test convert_to_float() """

    print("--- Testing convert_to_float() ---")

    # expected values
    expected = {"4.2": 4.2, "blanks": np.nan}

    # actual values
    actual = {"4.2": convert_to_float(value = "4.2", helper_str = "My help message"), "blanks": convert_to_float(value = "", helper_str = "My help message")}

    # print results
    _print_test_info(actual, expected)
    
def test_rmspecialchars():
    """ Test rmspecialchars() """

    print("--- Testing rmspecialchars() ---") 

    # expected values
    expected = {"*6.5_": "6.5", "blanks": "", "*$^**(@4.2_+;": "4.2", "-3.6": "-3.6"}

    # actual values
    actual = {"*6.5_": rmspecialchars("*6.5_"), "blanks": rmspecialchars(""), "*$^**(@4.2_+;": rmspecialchars("*$^**(@4.2_+;"), "-3.6": rmspecialchars("-3.6")}

    # print results
    _print_test_info(actual, expected)


def test_create_monthly_dict():
    """ Test create_monthly_dict """

    print("--- Testing create_monthly_dict ---")

    # expected values
    expected = {"January": [], "February": [], "March": [], "April": [], "May": [], "June": [], "July": [], "August": [], "September": [], "October": [], "November": [], "December": []}

    # actual values
    actual = create_monthly_dict()

    # print results
    _print_test_info(actual, expected)

    
def test_subset_data():
    """ Test subset_data() """

    print("--- Testing subset_data() for dates within start date and end date ---")

    # expected values
    expected = {"dates_within_range": [datetime.datetime(2014, 1, 4, 0, 0), datetime.datetime(2014, 1, 5, 0, 0),
                                       datetime.datetime(2014, 1, 6, 0, 0), datetime.datetime(2014, 1, 7, 0, 0),
                                       datetime.datetime(2014, 1, 8, 0, 0), datetime.datetime(2014, 1, 9, 0, 0), 
                                       datetime.datetime(2014, 1, 10, 0, 0)],
                "values_within_range": np.array([3, 4, 5, 6, 7, 8, 9]),
  
                "dates_outside_range": [datetime.datetime(2014, 1, 1, 0, 0), datetime.datetime(2014, 1, 2, 0, 0), datetime.datetime(2014, 1, 3, 0, 0),
                                        datetime.datetime(2014, 1, 4, 0, 0), datetime.datetime(2014, 1, 5, 0, 0),
                                        datetime.datetime(2014, 1, 6, 0, 0), datetime.datetime(2014, 1, 7, 0, 0),
                                        datetime.datetime(2014, 1, 8, 0, 0), datetime.datetime(2014, 1, 9, 0, 0), 
                                        datetime.datetime(2014, 1, 10, 0, 0), datetime.datetime(2014, 1, 11, 0, 0)],
                "values_outside_range": np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    } 

    # data for subset_data function
    dates = np.array([datetime.datetime(2014, 01, 01) + datetime.timedelta(i) for i in range(11)])
    
    values = np.array([i for i in range(11)])    

    # actual values
    actual = {}    
    actual["dates_within_range"], actual["values_within_range"] = subset_data(dates, values, start_date = datetime.datetime(2014, 01, 04), end_date = datetime.datetime(2014, 01, 10))

    actual["dates_outside_range"], actual["values_outside_range"] = subset_data(dates, values, start_date = datetime.datetime(2013, 12, 01), end_date = datetime.datetime(2014, 01, 20))

    # print results
    _print_test_info(actual, expected)
  

def test_find_start_end_dates1():
    """ Testing find_start_end_dates() """    
    
    print("--- Testing find_start_end_dates() part 1 ---")    

    # expected values
    expected = {"start_date": datetime.datetime(2014, 01, 03), "end_date": datetime.datetime(2014, 01, 11)} 


    # first element of dates2 being 2 days later than first element of dates1")   
    dates1 = [datetime.datetime(2014, 01, 01) + datetime.timedelta(i) for i in range(11)]
    dates2 = [datetime.datetime(2014, 01, 03)+ datetime.timedelta(i) for i in range(11)]

    # actual values
    actual = {}    
    actual["start_date"], actual["end_date"] = find_start_end_dates(dates1, dates2)

    # print results
    _print_test_info(actual, expected)

def test_find_start_end_dates2():
    """ Testing find_start_end_dates() """    
    
    print("--- Testing find_start_end_dates() part 2 ---")    

    # expected values
    expected = {"start_date": datetime.datetime(2014, 01, 04), "end_date": datetime.datetime(2014, 01, 12)} 


    # first element of dates1 being 2 days later than first element of dates1")   
    dates1 = [datetime.datetime(2014, 01, 04) + datetime.timedelta(i) for i in range(11)]
    dates2 = [datetime.datetime(2014, 01, 02)+ datetime.timedelta(i) for i in range(11)]

    # actual values
    actual = {}    
    actual["start_date"], actual["end_date"] = find_start_end_dates(dates1, dates2)

    # print results
    _print_test_info(actual, expected)
       
    
def main():
    """ Test functionality of helpers """

    test_now()

    test_get_filepaths()    
      
    test_get_file_info()
    
    test_make_directory()
    
    test_isfloat()

    test_convert_to_float()

    test_rmspecialchars()

    test_create_monthly_dict()
    
    test_subset_data()
    
    test_find_start_end_dates1()

    test_find_start_end_dates2()
    
if __name__ == "__main__":
    main()        
    
    