# -*- coding: utf-8 -*-
"""
:Module: nwispy_helpers.py

:Author: Jeremiah Lant
 
:Email: jlant@usgs.gov

:Purpose: 

Collection of helper functions. 

"""
import os
import numpy as np
import datetime

def now():
    """    
    Return current date and time in a format that can be used as a file name. 
    Format: year-month-day_hour.minute.second.microsecond (microsecond is sliced to display 3 digits instead of 6)
    Example 2014-03-18_15.51.46.252
        
    Parameters
    ----------
        **none**
      
    Return
    ------
        **date_time** : string of date and time
        
    """  
    date_time = datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f")[:-4]
    
    return date_time

def get_file_paths(directory, file_ext = None):
    """    
    Return a list of full file paths from a directory including its subdirectories.
        
    Parameters
    ----------    
        **directory** : string path 
      
    Return
    ------
        **file_paths** : list of full file paths from a directory
        
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
        **path** : string path name
      
    Return
    ------
        **filedir** : string file directory path
        **filename** : string file name
        
    """ 
    filedir, filename = os.path.split(path)
    
    # filedir is an empty string when file is in current directory 
    if not filedir: 
        filedir = os.getcwd()

    return filedir, filename

def make_directory(path, directory_name):
    """    
    Make an output directory.
    
    Parameters
    ----------
        **path**: string path name
        **directory_name** : string directory name
      
    Return
    ------
        **directory_path** : string path to directory 
        
    """    
#    directory_path = '/'.join([path, directory_name])
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
        **value** : string
        
    Return
    ------
        **boolean**
        
    """
    
    try:
        float(value)
        return True
        
    except ValueError:
        return False

def subset_data(dates, values, start_date, end_date):
    """   
    Subset the *dates* and *values* arrays to match the range of the *start_date*
    and *end_date*. If *start_date* and *end_date* are not within the range of dates
    specified in *dates*, then the *start_date* and *end_date* are set to the
    first and last dates in the array *dates*.
            
    Parameters 
    ----------
        **dates** :  array of dates as datetime objects 
        
        **data** : array of data
        
        **start_date** : datetime object
        
        **end_date** : datetime object
    
    Return
    ------
        **(subset_dates, subset_values)** : tuple of arrays of subset dates and values 

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
        **dates1** : list of datetime objects
        
        **dates2** : list of datetime objects
    
    Return
    ------
        **(start_date, end_date)** : tuple of datetimes

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

    print("Floats like {} expected : actual".format(2.5))
    print("    True: {}".format(isfloat(2.5)))
    print("Ints like {} expected : actual".format(2))
    print("    True: {}".format(isfloat(2)))
    print("String floats like {} expected : actual".format("2.5"))
    print("    True: {}".format(isfloat("2.5")))
    print("String ints like {} expected : actual".format("2"))
    print("    True: {}".format(isfloat("2")))
    print("Regular strings like {} expected : actual".format("hello world"))
    print("    False: {}".format(isfloat("hello world")))
    print("Characters mixed with floats like {} expected : actual".format("2.5_"))
    print("    False: {}".format(isfloat("2.5_")))
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
    print("Start date* expected : actual")
    print("    2014-01-03: {}".format(start_date))
    print("*End date* expected : actual")
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
    print("*Start date* expected : actual")
    print("    2014-01-03: {}".format(start_date))
    print("*End date* expected : actual")
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
        print("*Value Error* expected : actual")
        print("    No matching dates for find_start_end_dates() : {}".format(error.message))
        
    
def main():
    """ Test functionality of helpers """

    test_now()

    test_get_filepaths()    
      
    test_get_file_info()
    
    test_make_directory()
    
    test_isfloat()
    
    test_subset_data()
    
    test_find_start_end_dates()
    
if __name__ == "__main__":
    main()        
    
    