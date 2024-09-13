import logging
from logging.handlers import RotatingFileHandler

def setupLogging(ERROR, WARNING, INFO):
    logger = logging.getLogger('Logger')
    logDrt = r'C:\Users\ajani\Downloads\webscrapping 101\MyAutomationProject\Logs'
    logger.setLevel(logging.DEBUG)  # Capture all logs at DEBUG and above

    # Handler for INFO and DEBUG messages
    infoHandler = RotatingFileHandler(f'{logDrt}/{INFO}', maxBytes=10000, backupCount=5)
    infoHandler.setLevel(logging.INFO)
    infoFormatter = logging.Formatter('%(asctime)s - INFO - %(message)s')
    infoHandler.setFormatter(infoFormatter)

    # WARNING Handler
    warning_handler = RotatingFileHandler(f'{logDrt}/{WARNING}', maxBytes=10000, backupCount=5)
    warning_handler.setLevel(logging.WARNING)
    warning_format = logging.Formatter('%(asctime)s - %(name)s - WARNING - %(message)s')
    warning_handler.setFormatter(warning_format)

    # Handler for ERROR messages
    errorHandler = RotatingFileHandler(f'{logDrt}/{ERROR}', maxBytes=10000, backupCount=5)
    errorHandler.setLevel(logging.ERROR)
    errorFormatter = logging.Formatter('%(asctime)s - ERROR - %(message)s')
    errorHandler.setFormatter(errorFormatter)

    # Add handlers to the logger
    logger.addHandler(infoHandler)
    logger.addHandler(errorHandler)
    logger.addHandler(warning_handler)

    return logger