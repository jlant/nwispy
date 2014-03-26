import nose.tools
from nose import with_setup

import sys
import numpy as np
import datetime

# my module
from nwispy import nwispy_helpers



# define the global fixture to hold the data that goes into the functions you test
fixture = {}

def setup():
    """ Setup fixture for testing """

    print >> sys.stderr, "SETUP: nwispy_helpers tests"

    fixture["dates"] = np.array([datetime.datetime(2014, 01, 01) + datetime.timedelta(i) for i in range(11)])
    fixture["values"] = np.array([i for i in range(11)])

def teardown():
    """ Print to standard error when all tests are finished """
    
    print >> sys.stderr, "TEARDOWN: nwispy_helpers tests" 


#@with_setup(setup, teardown)

def test_subset_data_dates_within_range():
    
#    year = 2014
#    month = 01
#    day = 01
#    dates = np.array([datetime.datetime(int(year), int(month), int(day)) + datetime.timedelta(i) for i in range(11)])
#    
#    values = np.array([i for i in range(11)])    
    
    start = datetime.datetime(2014, 01, 04)
    end = datetime.datetime(2014, 01, 10)    
    
    expected_dates = np.array([datetime.datetime(2014, 1, 4, 0, 0), datetime.datetime(2014, 1, 5, 0, 0),
                               datetime.datetime(2014, 1, 6, 0, 0), datetime.datetime(2014, 1, 7, 0, 0),
                               datetime.datetime(2014, 1, 8, 0, 0), datetime.datetime(2014, 1, 9, 0, 0),
                               datetime.datetime(2014, 1, 10, 0, 0)])

    expected_values = np.array([3, 4, 5, 6, 7, 8, 9])
    
    actual_dates, actual_values = nwispy_helpers.subset_data(dates = fixture["dates"], 
                                                             values = fixture["values"], 
                                                             start_date = start, 
                                                             end_date = end)

    nose.tools.assert_equals(actual_dates.all(), expected_dates.all())
    nose.tools.assert_equals(actual_values.all(), expected_values.all())

def test_subset_data_dates_outside_range():
    
#    year = 2014
#    month = 01
#    day = 01
#    dates = np.array([datetime.datetime(int(year), int(month), int(day)) + datetime.timedelta(i) for i in range(11)])
#    
#    values = np.array([i for i in range(11)])    
    
    start = datetime.datetime(2013, 12, 01)
    end = datetime.datetime(2014, 01, 20)  
    
    expected_dates = np.array([datetime.datetime(2014, 1, 1, 0, 0), datetime.datetime(2014, 1, 2, 0, 0),
                               datetime.datetime(2014, 1, 3, 0, 0), datetime.datetime(2014, 1, 4, 0, 0),
                               datetime.datetime(2014, 1, 5, 0, 0), datetime.datetime(2014, 1, 6, 0, 0),
                               datetime.datetime(2014, 1, 7, 0, 0), datetime.datetime(2014, 1, 8, 0, 0),
                               datetime.datetime(2014, 1, 9, 0, 0), datetime.datetime(2014, 1, 10, 0, 0),
                               datetime.datetime(2014, 1, 11, 0, 0)])

    expected_values = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    
    actual_dates, actual_values = nwispy_helpers.subset_data(dates = fixture["dates"], 
                                                             values = fixture["values"], 
                                                             start_date = start, 
                                                             end_date = end)

    nose.tools.assert_equals(actual_dates.all(), expected_dates.all())
    nose.tools.assert_equals(actual_values.all(), expected_values.all())
"""

    
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
    "" Testing find_start_end_dates functionality ""    
    
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
        
"""