"""
:Module: helpers.py

:Author: Jeremiah Lant
 
:Email: jlant@usgs.gov

:Purpose: 
Helper functions for the nwispy.py module.

"""

def is_float(value):
    """   
    Determine if string value can be converted to a float. Return True if
    value can be converted to a float and False otherwise.
    
    *Parameters*:
        value: string
        
    *Return*:
        boolean
        
    """
    
    try:
        float(value)
        return True
        
    except ValueError:
        return False