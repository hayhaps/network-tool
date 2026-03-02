#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块
功能：日志记录和管理
"""

import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler


class NetworkToolLogger:
    def __init__(self, name='NetworkTool', log_dir='logs'):
        self.name = name
        self.log_dir = log_dir
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, f'{name}_{datetime.now().strftime("%Y%m%d")}.log')
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def debug(self, message):
        self.logger.debug(message)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def critical(self, message):
        self.logger.critical(message)
    
    def log_operation(self, operation, target, result):
        log_message = f"操作: {operation} | 目标: {target} | 结果: {result}"
        self.info(log_message)
    
    def log_error(self, operation, target, error):
        log_message = f"操作: {operation} | 目标: {target} | 错误: {error}"
        self.error(log_message)


logger = NetworkToolLogger()


def get_logger():
    return logger


def log_info(message):
    logger.info(message)


def log_error(message):
    logger.error(message)


def log_warning(message):
    logger.warning(message)


def log_debug(message):
    logger.debug(message)


def log_operation(operation, target, result):
    logger.log_operation(operation, target, result)


def log_error_operation(operation, target, error):
    logger.log_error(operation, target, error)
