#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time   : 2025/11/11 20:37
@Author : YangFei
@File   : cn_clip.py
@Desc   : Chinese-CLIP 多模态向量模型
"""
import os
import logging
import torch
from typing import List, Optional
from functools import lru_cache
from torchvision.transforms import Compose
from cn_clip.clip import load_from_name, tokenize
from cn_clip.clip.model import CLIP


from core.exceptions import BasRequestException

logger = logging.getLogger(__name__)


class ChineseCLIP:
    """Chinese-CLIP 多模态向量模型"""

    def __init__(self):
        """初始化 Chinese-CLIP 模型实例"""
        self._model: Optional[CLIP] = None
        self._preprocess: Optional[Compose] = None
        # 当前的模型name
        self._model_type: str = ''
        # 预定义模型配置
        self._model_configs = {
            "mini": "RN50",  # 迷你版, 速度最快，适用于开发测试场景
            "base": "ViT-B-16",  # 基础版, 性能均衡，适用于大多数场景
            "large": "ViT-L-14",  # 标准版, 高精度，适用于对精度要求较高的场景
            "large-hd": "ViT-L-14-336",  # 高清版, 更高分辨率，适用于细节要求高的场景
            "huge": "ViT-H-14"  # 旗舰版, 最高精度，适用于极致性能场景
        }

    async def init(self, model_type: str = "mini", model_dir: str = "models/pretrained_weights"):
        """初始化服务，加载所有模型"""
        if self._model is not None:
            logger.warning('Chinese-CLIP 模型实例已经完成初始化。')
            return

        logger.info("🚀 开始初始化 Chinese-CLIP 模型实例...")

        # 标准化模型键
        model_key = model_type.strip().lower()
        # 保存模型类型
        self._model_type = model_key

        # 验证模型类型
        if model_key not in self._model_configs:
            raise BasRequestException(
                f"指定模型 {model_type} 不存在，可选项: {list(self._model_configs.keys())}")

        # 使用绝对路径
        abs_model_dir = os.path.abspath(model_dir)
        logger.info(f"📁 模型目录: {abs_model_dir}")

        try:
            # 判断是否使用 GPU
            device = "cuda" if torch.cuda.is_available() else "cpu"

            # 自动从 model_dir 查找对应的 .pt 文件
            model, preprocess = load_from_name(
                name=self._model_configs[model_key],
                device=device,
                download_root=abs_model_dir
            )

            # 切换到评估模式（关闭 dropout 等训练相关层）
            model.eval()

            # 保存模型和预处理器
            self._model = model
            self._preprocess = preprocess

            logger.info(f"✅  成功加载的模型类型 {model_key} -> {device}")

        except Exception as e:
            logger.error(f"❌ 加载模型 {model_key} 失败: {e}")
            raise

    async def switch_model(self, model_type: str = 'mini', model_dir: str = "models/pretrained_weights") -> None:
        """切换当前使用的模型"""
        logger.debug(f"🔄 切换 Chinese-CLIP 模型到 {model_type}...")

        # 标准化模型键
        model_key = model_type.strip().lower()

        if self._model_type and model_key != self._model_type:
            # 清理当前模型资源
            await self.shutdown()

            # 重新初始化模型
            await self.init(model_type=model_type, model_dir=model_dir)

            logger.info(f"✅ 成功切换到 {model_type} 模型。")
        else:
            logger.debug('已经是指定模型类型，无需切换。')

    async def shutdown(self) -> None:
        """关闭服务，清理资源"""
        self._model = None
        self._preprocess = None
        self._model_type = ''

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        get_clip.cache_clear()

        logger.info("Chinese-CLIP 模型实例资源已清理")

    def get_available_models(self) -> List[str]:
        """获取可用模型列表"""
        return list(self._model_configs.keys())

    def tokenize(self, texts: List[str]):
        """文本标记化"""
        # 使用 cn-clip 提供的 tokenize 函数
        return tokenize(texts)

    @property
    def model(self):
        """获取当前加载的模型"""
        if self._model is None:
            raise RuntimeError("Chinese-CLIP 模型实例未初始化")
        return self._model

    @property
    def preprocess(self):
        """获取当前模型的预处理器"""
        if self._preprocess is None:
            raise RuntimeError("Chinese-CLIP 模型实例未初始化")
        return self._preprocess


@lru_cache()
def get_clip() -> ChineseCLIP:
    """获取 Chinese-CLIP 模型实例"""
    return ChineseCLIP()
