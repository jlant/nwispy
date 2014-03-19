import logging
import os.path

def initialize_loggers(output_dir, logging_type = "warn"):
    
    # create main logger and set global log level to debug
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to INFO
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    if logging_type == "warn":
        # create file handler and set level to WARN - write to a file only if a message is sent to this handler
        handler = logging.FileHandler(os.path.join(output_dir, "warn.log"), "w", encoding = None, delay = "true")
        handler.setLevel(logging.WARN)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    elif logging_type == "exception":
        # create debug file handler and set level to debug - file will be created every run
        handler = logging.FileHandler(os.path.join(output_dir, "exception.log"), "w", encoding = None, delay = "true")
        handler.setLevel(logging.ERROR)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)        

      
def remove_loggers():
    
    logger = logging.getLogger()
    handlers_list = list(logger.handlers)
    for i in handlers_list:
        logger.removeHandler(i)
        i.flush()
        i.close()