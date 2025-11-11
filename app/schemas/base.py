#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/10 23:32
@Author : YangFei
@File   : base.py
@Desc   : 
"""
from typing import TypeVar, Generic, Optional
from pydantic import BaseModel, Field


# 定义泛型类型变量
T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """ 基础 API 响应结构，继承 BaseModel 并支持泛型 """
    code: int = 200  # 默认成功状态码
    msg: str = "success"  # 默认成功消息
    data: Optional[T | dict] = Field(default_factory=dict)  # 可选数据字段

    @staticmethod
    def success(data: Optional[T | dict] = None, msg: str = "success") -> "Response[T]":
        """ 成功消息，传递数据和可选消息，code 固定为 200 """
        return Response[T](
            code=200,
            msg=msg,
            data=data if data is not None else {}  # 成功时默认返回空字典
        )

    @staticmethod
    def fail(code: int, msg: str, data: Optional[T | dict] = None) -> "Response[T]":
        """ 失败消息，传递状态码和消息 """
        return Response[T](
            code=code,
            msg=msg,
            data=data if data is not None else {}  # 失败时默认返回空字典
        )
