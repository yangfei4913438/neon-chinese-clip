#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/10 23:14
@Author : YangFei
@File   : routes.py
@Desc   : 路由入口
"""
from fastapi import APIRouter
from .clip_routes import clip_router


def create_routes() -> APIRouter:
    """ 创建并返回应用的主路由器，包含所有子路由器 """
    # 创建主路由器
    main_router = APIRouter()

    # 包含多模态向量模块路由
    main_router.include_router(clip_router)

    # 返回主路由器
    return main_router


router = create_routes()
