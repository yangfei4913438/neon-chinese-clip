#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/10 23:14
@Author : YangFei
@File   : main.py
@Desc   : 入口文件
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.log_config import setup_logging
from core.cn_clip import get_clip

from app.endpoints import router
from app.errors import register_exception_handlers

# 2. 初始化日志系统
setup_logging(log_level=logging.DEBUG)
logger = logging.getLogger(__name__)



@asynccontextmanager
async def lifespan(app: FastAPI):
    """ 创建 FastAPI 应用的异步生命周期的上下文管理器 """
    # 启动时初始化资源
    logger.info("Neon CHINESE CLIP 正在初始化...")

    # 初始化 Chinese-CLIP 模型实例
    await get_clip().init(model_type='mini')

    try:
        # yield 之前的代码在应用启动时执行
        yield  # 生命周期中间点

        # yield 之后的代码在应用关闭时执行
    finally:
        # 关闭时释放资源
        logger.info("Neon CHINESE CLIP 正在关闭...")
        # 关闭 Chinese-CLIP 模型实例
        await get_clip().shutdown()


# 创建 FastAPI 应用实例
app = FastAPI(
    title="neon-chinese-clip",
    description="一个基于 Chinese-CLIP 的多模态向量服务。",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 6. 注册全局异常处理器
register_exception_handlers(app)

# 7. 导入并注册路由
app.include_router(router=router, prefix="/api")
