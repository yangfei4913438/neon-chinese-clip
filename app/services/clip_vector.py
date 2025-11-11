#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/11 10:33
@Author : YangFei
@File   : clip_vector_service.py
@Desc   : Chinese-CLIP 多模态向量服务
"""
from core.exceptions import InternalServerException, AppException
import io
import logging
import torch

from typing import List
from PIL import Image
from functools import lru_cache

from core.cn_clip import get_clip

logger = logging.getLogger(__name__)


class ClipVectorService:
    """Chinese-CLIP 多模态向量服务"""

    def __init__(self):
        """初始化 Chinese-CLIP 服务实例"""
        # 获取模型实例
        self._client = None

    async def init(self, model_name: str = None):
        """ 初始化服务 """
        if self._client:
            return
        # 获取模型实例
        self._client = get_clip()
        # 判断是否存在这个模型
        if model_name:
            # 切换到指定模型
            await self._client.switch_model(model_type=model_name)

    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return self._client.get_available_models()

    async def switch_model(self, model_type: str):
        """切换模型"""
        await self._client.switch_model(model_type)

    async def encode_text(self, texts: List[str]) -> List[List[float]]:
        """文本向量化"""
        try:
            model = self._client.model
            text_tokens = self._client.tokenize(texts)
            text_tokens = text_tokens.to(next(model.parameters()).device)

            with torch.no_grad():
                # 编码文本
                text_features = model.encode_text(text_tokens)
                # 计算文本向量的范数
                text_norm = text_features.norm(dim=1, keepdim=True)
                # 归一化向量
                text_features = text_features / text_norm

            # 返回文本向量列表
            return text_features.cpu().numpy().tolist()

        except AppException as ae:
            raise ae

        except Exception as e:
            logger.error(f"文本向量化失败: {e}")
            raise InternalServerException("文本向量化失败")

    async def encode_text_batch(self, texts: List[str]) -> List[List[float]]:
        """ 批量文本向量化（兼容现有接口）"""
        return await self.encode_text(texts)

    async def encode_image(self, image_data: bytes) -> List[float]:
        """图像向量化"""
        try:
            model = self._client.model
            preprocess = self._client.preprocess

            image = Image.open(io.BytesIO(image_data)).convert("RGB")

            # 调用 Compose 对象处理图像，返回 tensor
            image_tensor: torch.Tensor = preprocess(image)  # type: ignore

            # 增加 batch 维度
            image_tensor = image_tensor.unsqueeze(0)
            # 将图像张量移动到模型所在设备
            image_tensor = image_tensor.to(next(model.parameters()).device)

            # 进行图像编码
            with torch.no_grad():
                # 编码图像
                image_features = model.encode_image(image_tensor)
                # 计算图像向量的范数
                image_norm = image_features.norm(dim=1, keepdim=True)
                # 归一化向量
                image_features = image_features / image_norm

            # 返回图像向量列表
            return image_features.cpu().numpy()[0].tolist()

        except AppException as ae:
            raise ae

        except Exception as e:
            logger.error(f"图像向量化失败: {e}")
            raise InternalServerException("图像向量化失败")

    async def encode_image_batch(self, image_data_list: List[bytes]) -> List[List[float]]:
        """批量图像向量化"""
        try:
            results = []
            for image_data in image_data_list:
                vector = await self.encode_image(image_data)
                results.append(vector)
            return results
        except Exception as e:
            logger.error(f"批量图像向量化失败: {e}")
            raise InternalServerException("批量图像向量化失败")


@lru_cache()
def get_vector_service() -> ClipVectorService:
    """ 获取向量服务实例（单例） """
    return ClipVectorService()
