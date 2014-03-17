import logging

# create logger
module_logger = logging.getLogger("main_application.mymodule")

def helloworld():
    module_logger.info("this is an error in mymodule.helloworld")

