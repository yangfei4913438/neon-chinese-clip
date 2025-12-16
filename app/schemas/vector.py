#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/16 12:48
@Author : YangFei
@File   : vector.py
@Desc   : 向量请求结构, 文件上传的不能使用 pydantic 模型来处理，需要直接写在路由里面
"""
from typing import List
from pydantic import BaseModel, Field


class TextVectorRequest(BaseModel):
    """文本向量请求"""
    texts: List[str] = Field(..., description="要编码的文本列表")
    model_type: str = Field(default="mini", description="使用的模型类型")