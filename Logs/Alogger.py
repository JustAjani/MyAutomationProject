import logging
from logging.handlers import RotatingFileHandler
import asyncio
import aiofiles

class AsyncLoggingHandler(logging.Handler):
    def __init__(self, loop, filename, level=logging.NOTSET):
        super().__init__(level)
        self.loop = loop
        self.queue = asyncio.Queue()
        self.filename = filename
        self._task = loop.create_task(self._consume())

    async def _consume(self):
        while True:
            record = await self.queue.get()
            try:
                msg = self.format(record)
                async with aiofiles.open(self.filename, 'a') as f:
                    await f.write(msg + '\n')
            except Exception as e:
                print(f"Logging error: {e}")
            self.queue.task_done()

    def emit(self, record):
        # Schedule the put operation in the event loop
        self.loop.call_soon_threadsafe(self.queue.put_nowait, record)

def setupLogging(ERROR, WARNING, INFO, CRITICAL, async_mode=False):
    logger = logging.getLogger('Logger')
    logDrt = r'C:\Users\ajani\Downloads\webscrapping 101\MyAutomationProject\Logs'
    logger.setLevel(logging.DEBUG)  # Capture all logs at DEBUG and above

    if async_mode:
        loop = asyncio.get_event_loop()

        # Handler for INFO and DEBUG messages
        infoHandler = AsyncLoggingHandler(loop, f'{logDrt}/{INFO}', level=logging.INFO)
        infoFormatter = logging.Formatter('%(asctime)s - INFO - %(message)s')
        infoHandler.setFormatter(infoFormatter)

        # WARNING Handler
        warning_handler = AsyncLoggingHandler(loop, f'{logDrt}/{WARNING}', level=logging.WARNING)
        warning_format = logging.Formatter('%(asctime)s - %(name)s - WARNING - %(message)s')
        warning_handler.setFormatter(warning_format)

        # Handler for ERROR messages
        errorHandler = AsyncLoggingHandler(loop, f'{logDrt}/{ERROR}', level=logging.ERROR)
        errorFormatter = logging.Formatter('%(asctime)s - ERROR - %(message)s')
        errorHandler.setFormatter(errorFormatter)

        # Handler for CRITICAL messages
        criticalHandler = AsyncLoggingHandler(loop, f'{logDrt}/{CRITICAL}', level=logging.CRITICAL)
        criticalFormatter = logging.Formatter('%(asctime)s - CRITICAL - %(message)s')
        criticalHandler.setFormatter(criticalFormatter)
    else:
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

        # Handler for CRITICAL messages
        criticalHandler = RotatingFileHandler(f'{logDrt}/{CRITICAL}', maxBytes=10000, backupCount=5)
        criticalHandler.setLevel(logging.CRITICAL)
        criticalFormatter = logging.Formatter('%(asctime)s - CRITICAL - %(message)s')
        criticalHandler.setFormatter(criticalFormatter)

    # Remove any existing handlers
    logger.handlers = []

    # Add handlers to the logger
    logger.addHandler(infoHandler)
    logger.addHandler(warning_handler)
    logger.addHandler(errorHandler)
    logger.addHandler(criticalHandler)

    return logger
