#!/use/bin/env python3.10
# coding:utf-8

"""
@version: 3.10
@author: huluobo
@file: log.py
@time: 2024/1/17 18:28
"""
import logging
from logging.handlers import RotatingFileHandler
import os


# 创建一个logger对象
logger = logging.getLogger(__name__)  # 建议使用__name__获取当前模块名作为logger的名称
logger.setLevel(logging.DEBUG)  # 设置日志级别，可以是DEBUG, INFO, WARNING, ERROR, CRITICAL等

# 创建一个文件处理器（将日志写入到my_log.log文件）
# 创建 log 目录
log_dir = 'log'
os.makedirs(log_dir, exist_ok=True)

# 创建一个可轮换的文件处理器
log_file_path = os.path.join(log_dir, 'my_log.log')
max_log_size = 100 * 1024  # 100 KB
# logging_active = True  # 默认为True，表示启动应用程序时开始日志记录
# file_handler = logging.FileHandler('my_log.log')
file_handler = RotatingFileHandler(log_file_path, maxBytes=max_log_size, backupCount=500)
file_handler.setLevel(logging.INFO)  # 可以为不同的处理器设置不同级别的日志输出

# 创建一个控制台处理器（将日志打印到屏幕）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # 控制台输出所有DEBUG及更高级别的日志

# 创建一个日志格式器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 给处理器添加格式器
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 将处理器添加到logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)