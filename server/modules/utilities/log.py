# coding: utf-8




# 既成のモジュールをインポートする.
import os
import sys
import logging
from logging.handlers import RotatingFileHandler




class CustomLogger:
    def __init__(self, log_file, max_bytes=1 * 1024 * 1024, backup_count=1):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.propagate = False

    def logging__debug(self, message):
        try:
          self.logger.debug(message)
        except:
          return "NG"
        return "OK"

    def logging__info(self, message):
        try:
          self.logger.info(message)
        except:
          return "NG"
        return "OK"

    def logging__warning(self, message):
        try:
          self.logger.warning(message)
        except:
          return "NG"
        return "OK"

    def logging__error(self, message):
        try: 
          self.logger.error(message)
        except:
          return "NG"
        return "OK"

    def logging__critical(self, message):
        try:
          self.logger.critical(message)
        except:
          return "NG"
        return "OK"