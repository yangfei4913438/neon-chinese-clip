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
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.schemas.base import Response
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

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(req: Request, e: RequestValidationError) -> JSONResponse:
        """ 处理请求验证异常，返回统一的错误响应 """
        # 记录异常日志
        logger.warning(f"捕获到请求验证异常: {e.errors()}")
        errors = e.errors()
        missing_fields = set()  # 用集合去重，避免同一字段多次报错
        other_errors = []

        # 遍历所有错误，分类处理
        for err in errors:
            loc = err["loc"]  # 字段位置，如 ("body", "file")、("query", "page")、("path", "id")
            err_type = err["type"]  # 错误类型，如 "missing"、"type_error"、"value_error"
            err_msg = err["msg"]  # 原始错误信息

            # 1. 处理「必填字段缺失」错误
            if err_type == "missing":
                # 提取字段名（loc 最后一个元素，如 "file"、"username"）
                field_name = loc[-1]
                missing_fields.add(field_name)
            # 2. 处理其他错误（类型错误、格式错误等）
            else:
                # 拼接字段位置+错误信息，如 "body.model_type: Input should be a valid string"
                field_path = ".".join(map(str, loc))  # 把 ("body", "model_type") 转成 "body.model_type"
                other_errors.append(f"{field_path}：{err_msg}")

        # 动态生成提示语
        if missing_fields:
            # 多个缺失字段："必填字段缺失：file、model_type（通过对应方式传递）"
            # 单个缺失字段："必填字段缺失：file（通过对应方式传递）"
            field_str = "、".join(missing_fields)
            # 可选：根据请求头判断传递方式（form-data/json/query），更精准
            content_type = req.headers.get("Content-Type", "")
            if "multipart/form-data" in content_type:
                transfer_tip = "（通过 form-data 传递）"
            elif "application/json" in content_type:
                transfer_tip = "（通过 JSON 请求体传递）"
            else:
                transfer_tip = ""

            msg = f"必填字段缺失：{field_str} {transfer_tip}"
        elif other_errors:
            # 其他验证错误："请求参数错误：body.model_type：Input should be a valid string"
            msg = f"请求参数错误：{'；'.join(other_errors)}"
        else:
            # 兜底提示
            msg = "请求参数验证失败，请检查字段格式和必填项"

        # 记录日志（保留原始错误信息，便于排查）
        logger.warning(f"捕获到参数验证异常: {msg} | 原始错误详情: {errors}")

        # 复用统一响应格式
        error_content = Response(code=400, msg=msg).model_dump()
        return JSONResponse(
            status_code=400,
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
