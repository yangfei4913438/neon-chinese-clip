#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/11 10:34
@Author : YangFei
@File   : clip_routes.py
@Desc   : Chinese-CLIP 多模态向量路由
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form, File

from app.schemas.base import Response
from app.schemas.vector import TextVectorRequest
from core.exceptions import ValidationException
from app.service_dependencies import get_vector_service

logger = logging.getLogger(__name__)


# 创建路由
clip_router = APIRouter(prefix="/clip", tags=["多模态向量模块"])


@clip_router.get(
    "/models",
    response_model=Response,
    summary="获取可用模型类型",
    description="获取所有可用的 Chinese-CLIP 模型类型列表。"
)
async def get_available_models(
    vector_service = Depends(get_vector_service)
):
    """获取可用模型类型列表"""
    try:
        models = vector_service.get_available_models()
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
        request: TextVectorRequest,
        vector_service = Depends(get_vector_service)
):
    """文本编码接口"""
    try:
        if not request.texts:
            raise ValidationException("文本列表不能为空")

        await vector_service.switch_model(request.model_type)

        embeddings = await vector_service.encode_text(request.texts)

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
        logger.error(f"文本编码失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="文本编码失败")


@clip_router.post(
    "/encode/image",
    response_model=Response,
    summary="图像向量化",
    description="将图像转换为向量表示。"
)
async def encode_image(
        file: UploadFile = File(..., description="上传的图像文件"),
        model_type: str = Form("mini", description="使用的模型类型"),
        vector_service = Depends(get_vector_service)
):
    """图像编码接口，注：file 和 model_type，通过 form-data 传递"""
    try:
        logger.debug(f'接收到的文件: {file}, 模型类型: {model_type}')
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise ValidationException("请上传图像文件")

        image_data = await file.read()
        if len(image_data) == 0:
            raise ValidationException("上传的文件为空")

        await vector_service.switch_model(model_type)

        embedding = await vector_service.encode_image(image_data)

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

