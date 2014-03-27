"""
:Module: nwispy_logging.py

:Author: Jeremiah Lant, jlant@usgs.gov, U.S. Geological Survey, Kentucky Water Science Center, http://www.usgs.gov/ 
 
:Synopsis: Handles logging of errors.
"""

__author__   = "Jeremiah Lant, jlant@usgs.gov, U.S. Geological Survey, Kentucky Water Science Center."
__copyright__ = "http://www.usgs.gov/visual-id/credit_usgs.html#copyright"
__license__   = __copyright__
__contact__   = __author__

import logging
import os

def initialize_loggers(output_dir):
    """    
    Initialize logging objects.
    
    Parameters
    ----------        
    output_dir : str
        String path 
    """ 
    # create main logger and set global log level to debug
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to INFO
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create file handler and set level to WARN - write to a file only if a message is sent to this handler
    handler = logging.FileHandler(os.path.join(output_dir, "error.log"), "w", encoding = None, delay = "true")
    handler.setLevel(logging.WARN)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)    

      
def remove_loggers():
    """    
    Remove all logging objects.       
    """     
    logger = logging.getLogger()
    handlers_list = list(logger.handlers)
    for i in handlers_list:
        logger.removeHandler(i)
        i.flush()
        i.close()


def test_logging():
    """ Test functionality of logging errors """
    
    print("--- Testing logging ---")
    # initialize error logging
    initialize_loggers(output_dir = os.getcwd())
    
    # creat a warning log
    logging.warn("my warning log")

    # creat a warning log
    logging.error("my error log")

    # creat a warning log; will print and log None here because there is no real exception
    logging.exception("my exception log")
    
    # try to add info log; info should NOT be added to warn.log since it is not setup for logging.info
    logging.info("my info log")
    
    # try to add debug log; debug should NOT be added to warn.log since it is not setup for logging.debug
    logging.debug("my debug log")

    # close error logging
    remove_loggers()

    print("Logging finished. Check current working directory for warn.log")   
    print("")

def main():
    """ Test functionality of logging errors """
    
    test_logging()
    
if __name__ == "__main__":
    main()