#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/10 23:14
@Author : YangFei
@File   : exceptions.py
@Desc   : 应用程序异常定义
"""

from typing import Any


class AppException(RuntimeError):
    """ 应用程序运行时异常基类 """

    def __init__(self, code: int = 400, status_code: int = 400, msg: str = '应用程序异常', data: Any = None):
        """ 构造函数
        :param code: 自定义业务错误码，默认 400
        :param status_code: 状态码，默认 400
        :param msg: 错误消息，默认 '应用程序异常'
        :param data: 附加数据，默认 None
        """
        self.code = code
        self.status_code = status_code
        self.msg = msg
        self.data = data
        super().__init__()


class BasRequestException(AppException):
    """ 客户端请求异常类，继承自 AppException """

    def __init__(self, msg: str = '客户端请求错误，请检查后重试.'):
        """ 初始化请求异常实例
        :param msg: 错误消息，默认 '客户端请求错误，请检查后重试.'
        """
        super().__init__(msg=msg, code=400, status_code=400)


class NotFoundException(AppException):
    """ 资源未找到异常类，继承自 AppException """

    def __init__(self, msg: str = '请求的资源未找到, 请检查后重试.'):
        """ 初始化未找到异常实例
        :param msg: 错误消息，默认 '请求的资源未找到, 请检查后重试.'
        """
        super().__init__(msg=msg, code=404, status_code=404)


class ValidationException(AppException):
    """ 数据验证异常类，继承自 AppException """

    def __init__(self, msg: str = '数据验证失败，请检查输入后重试.'):
        """ 初始化数据验证异常实例
        :param msg: 错误消息，默认 '数据验证失败，请检查输入后重试.'
        """
        super().__init__(msg=msg, code=422, status_code=422)


class TooManyRequestsException(AppException):
    """ 请求过多异常类，继承自 AppException """

    def __init__(self, msg: str = '请求过多，请稍后重试.'):
        """ 初始化请求过多异常实例
        :param msg: 错误消息，默认 '请求过多，请稍后重试.'
        """
        super().__init__(msg=msg, code=429, status_code=429)


class InternalServerException(AppException):
    """ 服务器内部异常类，继承自 AppException """

    def __init__(self, msg: str = '服务器内部错误，请稍后重试.'):
        """ 初始化服务器内部异常实例
        :param msg: 错误消息，默认 '服务器内部错误，请稍后重试.'
        """
        super().__init__(msg=msg, code=500, status_code=500)
