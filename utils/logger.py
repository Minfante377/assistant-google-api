from datetime import datetime
import os


class Logger:

    def __init__(self, log_path):
        """
        Inits Logger singleton to be used globally.

        Args:
            - log_path(str): log file full path.

        """
        log_path = os.path.join(log_path, "log.txt")
        self.log_file = open(log_path, "a+")

    def log_info(self, info):
        now = datetime.now()
        now_formated = now.strftime("%d-%m-%Y %H:%M:%S")
        self.log_file.write("[{} INFO]: {}\n".format(now_formated, info))

    def log_error(self, error):
        now = datetime.now()
        now_formated = now.strftime("%d-%m-%Y %H:%M:%S")
        self.log_file.write("[{} ERROR]: {}\n".format(now_formated, error))


logger = Logger(os.getcwd())
