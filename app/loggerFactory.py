import logging


class LoggerFactory(object):
    _LOG = None

    @staticmethod
    def __create_logger(name):
        """
        A private method that interacts with the python
        logging module
        """
        # set the logging format
        log_format = "%(asctime)s:%(levelname)s:%(message)s"

        # Initialize the class variable with logger object
        LoggerFactory._LOG = logging.getLogger(name)
        # Default is WARNING
        LoggerFactory._LOG.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        LoggerFactory._LOG.addHandler(ch)

        return LoggerFactory._LOG

    @staticmethod
    def get_logger(name):
        """
        A static method called by other modules to initialize logger in
        their own module
        """
        logger = LoggerFactory.__create_logger(name)

        # return the logger object
        return logger
