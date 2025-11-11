#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/10 23:14
@Author : YangFei
@File   : exception_handles.py
@Desc   : 全局异常处理
"""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.schemas import Response
from core.exceptions import AppException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    """ 注册全局异常处理器 """

    @app.exception_handler(AppException)
    async def app_exception_handler(req: Request, e: AppException) -> JSONResponse:
        """ 处理应用程序异常，返回统一的错误响应 """
        # 记录异常日志
        logger.error(f"捕获到应用程序异常: {e.msg}")

        # 组装错误响应内容
        error_content = Response(code=e.status_code, msg=e.msg).model_dump()

        # 返回 JSON 响应
        return JSONResponse(
            status_code=e.status_code,
            content=error_content,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(req: Request, e: HTTPException) -> JSONResponse:
        """ 处理 HTTP 异常，返回统一的错误响应 """
        # 记录异常日志
        logger.warning(f"捕获到 HTTP 异常: {e.detail}")

        # 组装错误响应内容
        error_content = Response(code=e.status_code, msg=e.detail).model_dump()

        # 返回 JSON 响应
        return JSONResponse(
            status_code=e.status_code,
            content=error_content,
        )

    @app.exception_handler(Exception)
    async def exception_handler(req: Request, e: Exception) -> JSONResponse:
        """ 处理未捕获的异常，返回统一的错误响应 """
        # 记录异常日志
        logger.error(f"捕获到异常: {e}")

        # 组装错误响应内容
        error_content = Response(code=500, msg="服务器出现异常，请稍后重试。").model_dump()

        # 返回 JSON 响应
        return JSONResponse(
            status_code=500,
            content=error_content,
        )
