import logging
import time

# change this value to "INFO", "ERROR", etc. to adjust the logger level
LOG_LEVEL = "DEBUG"  

# custom formatter to include UTC timestamp, function name, level and message
class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        # Convert the timestamp to UTC
        utc_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(record.created))
        return utc_time

    def format(self, record):
        record.utc_timestamp = self.formatTime(record)
        record.func_name = record.funcName  # Function name from which the log is called
        return super().format(record)

class Logger:
    _instance = None  # Class attribute to store the Logger instance

    def __new__(cls, level="INFO"):
        if cls._instance is None:
            # If no instance exists, create one and initialize it
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialize_logger(level)
        return cls._instance

    def _initialize_logger(self, level):
        # Dictionary to map string log levels to their corresponding values
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        # Create a logger
        self.logger = logging.getLogger("custom_logger")

        # Set the logger level based on the input
        self.logger.setLevel(levels.get(level.upper(), logging.INFO))

        # Check if the logger already has handlers (to avoid duplicate handlers)
        if not self.logger.handlers:
            # Create a stream handler to print logs to stdout
            console_handler = logging.StreamHandler()

            # Set the custom format for the logs
            formatter = CustomFormatter(
                fmt="%(utc_timestamp)s | %(func_name)s | %(levelname)s | %(message)s"
            )
            console_handler.setFormatter(formatter)

            # Add the handler to the logger
            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger

logger = Logger(LOG_LEVEL)
logger = logger.get_logger()

# Example usage of the logger
def example_function(logger):
    logger.info("This is an info message.")
    logger.debug("This is a debug message.")
    logger.error("This is an error message.")

if __name__ == "__main__":
    # Call the example function to see logs at the specified level
    example_function(logger)
