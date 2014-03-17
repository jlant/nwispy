import logging

def setup_logging():

    
#    logging.basicConfig(filename = '/'.join([error_path, "file-errors.log"]), filemode = "w", level = logging.INFO)

    # create logger with 'spam_application'
    logger = logging.getLogger('main_application')
    logger.setLevel(logging.DEBUG)
    
    # create file handler which logs even debug messages
    fh = logging.FileHandler('file.log')
    fh.setLevel(logging.DEBUG)
    
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    
def shutdown_logging():
    logging.shutdown()
    
