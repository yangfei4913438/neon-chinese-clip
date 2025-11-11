#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/11 10:34
@Author : YangFei
@File   : clip_routes.py
@Desc   : Chinese-CLIP 多模态向量路由
"""
import logging
from fastapi import APIRouter, UploadFile, File, Form, Body, HTTPException, FastAPI
from typing import List
from contextlib import asynccontextmanager

from app.schemas import Response
from app.services.clip_vector import get_vector_service
from core.exceptions import ValidationException

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """ 创建 FastAPI 应用的异步生命周期的上下文管理器 """
    # 启动时初始化资源
    logger.info("CHINESE CLIP 路由 正在初始化...")

    # 获取单例服务并初始化
    service = get_vector_service()
    await service.init(model_name="mini")

    try:
        # yield 之前的代码在应用启动时执行
        yield  # 生命周期中间点

        # yield 之后的代码在应用关闭时执行
    finally:
        # 关闭时释放资源
        logger.info("CHINESE CLIP 路由 正在关闭...")


# 创建路由
clip_router = APIRouter(prefix="/clip", tags=["多模态向量模块"], lifespan=lifespan)



@clip_router.get(
    "/models",
    response_model=Response,
    summary="获取可用模型类型",
    description="获取所有可用的 Chinese-CLIP 模型类型列表。"
)
async def get_available_models():
    """获取可用模型类型列表"""
    try:
        clip_service = get_vector_service()
        models = clip_service.get_available_models()
        return Response.success(data={"models": models})
    except Exception as e:
        logger.error(f"获取模型类型列表失败: {e}")
        raise HTTPException(status_code=500, detail="获取模型类型列表失败")


@clip_router.post(
    "/encode/text",
    response_model=Response,
    summary="文本向量化",
    description="将文本转换为向量表示。"
)
async def encode_text(
        texts: List[str] = Body(..., description="要编码的文本列表"),
        model_type: str = Body("mini", description="使用的模型类型")
):
    """文本编码接口"""
    try:
        if not texts:
            raise ValidationException("文本列表不能为空")

        clip_service = get_vector_service()
        await clip_service.switch_model(model_type)

        embeddings = await clip_service.encode_text(texts)

        return Response.success(data={
            "embeddings": embeddings,
            "count": len(embeddings),
            "dimension": len(embeddings[0]) if embeddings else 0
        })

    except ValidationException:
        raise
    except ValueError as e:
        raise ValidationException(str(e))
    except Exception as e:
        logger.error(f"文本编码失败: {e}")
        raise HTTPException(status_code=500, detail="文本编码失败")


@clip_router.post(
    "/encode/image",
    response_model=Response,
    summary="图像向量化",
    description="将图像转换为向量表示。"
)
async def encode_image(
        file: UploadFile = File(..., description="上传的图像文件"),
        model_type: str = Form("mini", description="使用的模型类型")
):
    """图像编码接口"""
    try:
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise ValidationException("请上传图像文件")

        image_data = await file.read()
        if len(image_data) == 0:
            raise ValidationException("上传的文件为空")

        clip_service = get_vector_service()
        await clip_service.switch_model(model_type)

        embedding = await clip_service.encode_image(image_data)

        return Response.success(data={
            "embedding": embedding,
            "filename": file.filename,
            "dimension": len(embedding)
        })

    except ValidationException:
        raise
    except ValueError as e:
        raise ValidationException(str(e))
    except Exception as e:
        logger.error(f"图像编码失败: {e}")
        raise HTTPException(status_code=500, detail="图像编码失败")

