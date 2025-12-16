#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/12/16 11:53
@Author : YangFei
@File   : service_dependencies.py
@Desc   : 服务依赖注入
"""
from fastapi import Depends

from core.cn_clip import get_clip
from app.services.clip_vector import ClipVectorService


def get_vector_service(
    client = Depends(get_clip)
):
    """ 获取向量服务 """
    return ClipVectorService(client)