import logging
import mymodule
import config_logging


config_logging.setup_logging()

mymodule.helloworld()

config_logging.shutdown_logging()