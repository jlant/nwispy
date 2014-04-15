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

def now():
    """    
    Return current date and time in a format that can be used as a file name. 
    Format: year-month-day_hour.minute.second.microsecond; i.e. 2014-03-18_15.51.46.25
      
    Returns
    -------
    date_time : str
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
        
    Parameters
    ----------    
    directory : str
        String path 
      
    Returns
    -------
    file_paths : list 
        List of strings of full file paths from a directory.
    """     
    file_paths = []  

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath) 

    # if user wants on certain file extentions then only include those paths by removing unwanted paths
    if file_ext:
        for f in file_paths:
            if not f.endswith(file_ext):
                file_paths.remove(f)

    return file_paths

def get_file_info(path):
    """    
    Get file directory and name from a file path.
    
    Parameters
    ----------
    path : str
        String path
      
    Returns
    -------
    filedir : str
        String file directory path
    filename : str
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
    path: str
        String path 
    directory_name : str
        String name
      
    Returns
    -------
    directory_path : str
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
    value : str
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
    value : str
        String value to remove any existing characters from
        
    Returns
    -------
    value : str
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
    
def subset_data(dates, values, start_date, end_date):
    """   
    Subset the dates and values arrays to match the range of the start_date
    and end_date. If start_date and end_date are not within the range of dates
    specified in dates, then the start_date and end_date are set to the
    first and last dates in the array dates.
            
    Parameters 
    ----------
    dates :  array 
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


def test_now():
    """ Test now() functionality """

    print("--- Testing now() ---")    
    
    date_time_str = now()
    print("Right now is: ")
    print("    {}".format(date_time_str))
    print("")

def test_get_filepaths():
    """ Test get_filepaths functionality """
    
    print("--- Testing get_filepaths() ---")
    file_paths = get_file_paths(os.getcwd(), file_ext = ".py")
    
    print("File paths are:")
    print("    {}".format(file_paths))
    print("")

def test_get_file_info():
    """ Test get_file_info functionality """

    print("--- Testing get_file_info ---")  
    
    filedir, filename = get_file_info(path = os.path.join(os.getcwd(), "nwispy_helpers.py"))

    print("File directory is:")
    print("    {}".format(filedir))
    print("File name is expected : actual")
    print("    nwispy_helpers.py : {}".format(filename))
    print("")

def test_make_directory():
    """ Test make_directory() functionality"""

    print("---- Testing make_directory ----")  
    
    directory_path = make_directory(path = os.getcwd(), directory_name = "Testing")
    print("New directory path is:")
    print("    {}".format(directory_path))
    print("")

def test_isfloat():
    """ Test isfloat() functionality """

    print("--- Testing isfloat() ---") 

    print("Floats like {}\n    expected : actual".format(2.5))
    print("    True: {}".format(isfloat(2.5)))
    print("Ints like {}\n    expected : actual".format(2))
    print("    True: {}".format(isfloat(2)))
    print("String floats like {}\n    expected : actual".format("2.5"))
    print("    True: {}".format(isfloat("2.5")))
    print("String ints like {}\n    expected : actual".format("2"))
    print("    True: {}".format(isfloat("2")))
    print("Regular strings like {}\n    expected : actual".format("hello world"))
    print("    False: {}".format(isfloat("hello world")))
    print("Characters mixed with floats like {}\n    expected : actual".format("2.5_"))
    print("    False: {}".format(isfloat("2.5_")))
    print("")

def test_rmspecialchars():
    """ Test rmspecialchars functionality """

    print("--- Testing rmspecialchars() ---") 

    print("Floats like {}\n    expected : actual".format("*6.5_"))
    print("    6.5 : {}".format(rmspecialchars("*6.5_")))

    print("Empty strings like {}\n    expected : actual".format(""))
    print("    : {}".format(rmspecialchars("")))

    print("Floats like {}\n    expected : actual".format("*$^**(@4.2_+;"))
    print("    4.2 : {}".format(rmspecialchars("*$^**(@4.2_+;")))

    print("Floats like {}\n    expected : actual".format("-3.6"))
    print("    -3.6 : {}".format(rmspecialchars("-3.6")))
    
    print("")

def test_subset_data():
    """ Test subset_data() functionality """

    print("--- Testing subset_data() for dates within start date and end date ---")
    
    year = 2014
    month = 01
    day = 01
    dates = np.array([datetime.datetime(int(year), int(month), int(day)) + datetime.timedelta(i) for i in range(11)])
    
    values = np.array([i for i in range(11)])    
    
    start1 = datetime.datetime(2014, 01, 04)
    end1 = datetime.datetime(2014, 01, 10)
    
    subset_dates1, subset_values1 = subset_data(dates, values, start_date = start1, end_date = end1)
    
    print("*Dates* original")
    print("    {}".format(dates))
    print("*Values* original")
    print("    {}".format(values))
    print("*Start date* to *end date*")
    print("    {} to {}".format(start1, end1))
    print("*Dates* subset")
    print("    {}".format(subset_dates1))
    print("*Values* subset")
    print("    {}".format(subset_values1))
    print("")

    print("--- Testing subset_data() for dates NOT within start date and end date ---")
    
    start2 = datetime.datetime(2013, 12, 01)
    end2 = datetime.datetime(2014, 01, 20)
    
    subset_dates2, subset_values2 = subset_data(dates, values, start_date = start2, end_date = end2)
    
    print("*Dates* original")
    print("    {}".format(dates))
    print("*Values* original")
    print("    {}".format(values))
    print("*Start date* to *end date*")
    print("    {} to {}".format(start2, end2))
    print("*Dates* subset")
    print("    {}".format(subset_dates2))
    print("*Values* subset")
    print("    {}".format(subset_values2))
    print("")

def test_find_start_end_dates():
    """ Testing find_start_end_dates functionality """    
    
    print("--- Testing find_start_end_dates() for first element of dates2 being 2 days later than first element of dates1 ---")   
    year = 2014
    month = 01
    day1 = 01
    day2 = 03
    
    dates1 = [datetime.datetime(int(year), int(month), int(day1)) + datetime.timedelta(i) for i in range(11)]
    dates2 = [datetime.datetime(int(year), int(month), int(day2)) + datetime.timedelta(i) for i in range(11)]
    
    start_date, end_date = find_start_end_dates(dates1, dates2)
    print("Start date*\n    expected : actual")
    print("    2014-01-03: {}".format(start_date))
    print("*End date*\n    expected : actual")
    print("    2014-01-11: {}".format(end_date))
    print("")

    print("--- Testing find_start_end_dates() for first element of dates1 being 2 days later than first element of dates2 ---")    
    year = 2014
    month = 01
    day1 = 01
    day2 = 03
    
    dates1 = [datetime.datetime(int(year), int(month), int(day2)) + datetime.timedelta(i) for i in range(11)]
    dates2 = [datetime.datetime(int(year), int(month), int(day1)) + datetime.timedelta(i) for i in range(11)]
    
    start_date, end_date = find_start_end_dates(dates1, dates2)
    print("*Start date*\n    expected : actual")
    print("    2014-01-03: {}".format(start_date))
    print("*End date*\n    expected : actual")
    print("    2014-01-11: {}".format(end_date))
    print("")

    print("--- Testing find_start_end_dates() for NO MATCHING elements between dates1 and dates2 ---")

    try:
        year = 2014
        month1 = 01
        day1 = 01
        
        year = 2014
        month2 = 02
        day2 = 03
        
        dates1 = [datetime.datetime(int(year), int(month1), int(day1)) + datetime.timedelta(i) for i in range(11)]
        dates2 = [datetime.datetime(int(year), int(month2), int(day2)) + datetime.timedelta(i) for i in range(11)]
    
        start_date, end_date = find_start_end_dates(dates1, dates2)
        print("    PROBLEM exception was not executed")
        
    except ValueError as error:
        print("*Value Error*\n    expected : actual")
        print("    No matching dates for find_start_end_dates() : {}".format(error.message))
        
    
def main():
    """ Test functionality of helpers """

    test_now()

    test_get_filepaths()    
      
    test_get_file_info()
    
    test_make_directory()
    
    test_isfloat()

    test_rmspecialchars()
    
    test_subset_data()
    
    test_find_start_end_dates()
    
if __name__ == "__main__":
    main()        
    
    