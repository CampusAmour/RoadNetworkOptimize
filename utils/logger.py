#!/usr/bin/env python
# coding:utf-8
"""
Name   : logger.py
Author : CampusAmour
Contect: campusamour@gmail.com
Time   : 2022/3/12 23:52
"""
import os
import logging
import logging.handlers


class Logger(object):
    def __init__(self, log_name, level="DEBUG"):
        self.log_path = os.getcwd() + "//logs//" + log_name
        self.logger = logging.getLogger()
        self.logger.setLevel(level)
        self.fmt = "%(asctime)s [%(levelname)s][%(message)s][%(funcName)s,%(filename)s][line:%(lineno)d][tid:%(thread)d][pid:%(process)d]"
        if not os.path.exists(os.getcwd()+"//logs"):
            os.mkdir(os.getcwd()+"//logs")


    def _consoleHandle(self, level="INFO"):
        """控制台handler"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(self.fmt))
        return console_handler


    def _fileHandle(self, log_path, level="DEBUG"):
        """控制台handler"""
        file_handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=8*1024*1024, backupCount=16, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(self.fmt))

        return file_handler


    def getLogger(self):
        self.logger.addHandler(self._consoleHandle())
        self.logger.addHandler(self._fileHandle(self.log_path))
        return self.logger


if __name__ == "__main__":
    pass
