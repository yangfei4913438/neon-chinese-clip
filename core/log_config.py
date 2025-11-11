#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/10 23:14
@Author : YangFei
@File   : log_config.py
@Desc   : 日志配置项
"""
import logging
import datetime
import colorlog

class MicrosecondFormatter(colorlog.ColoredFormatter):
    def formatTime(self, record, datefmt=None):
        # 生成包含微秒的时间对象
        ct = datetime.datetime.fromtimestamp(record.created)
        # 自定义格式化时间字符串
        if datefmt:
            s = ct.strftime(datefmt)
        else:
            # 默认格式（包含微秒, 保留到毫秒）
            s = ct.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        return s


def setup_logging(log_level: int = logging.INFO):
    """ 配置日志系统，涵盖日志等级、输出格式、输出位置等 """

    # 1、获取根日志处理器
    root_logger = logging.getLogger()
    # 清空已有处理器（避免重复输出）
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # 2、设置日志等级
    root_logger.setLevel(log_level)

    # 3、创建日志格式化器
    log_formatter = MicrosecondFormatter(
        # 日志输出格式，包含时间、日志器名称、日志等级和日志消息
        fmt="[%(asctime)s] - %(name)s:%(lineno)d - %(log_color)s%(levelname)s%(reset)s - %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
        # 重置颜色，避免颜色影响后续输出
        reset=True,
    )

    # 4、创建控制台处理器并设置格式化器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(log_level)

    # 5、将处理器添加到根日志处理器
    root_logger.addHandler(console_handler)

    # 6、日志系统初始化完成提示
    root_logger.info("日志系统初始化完成")
