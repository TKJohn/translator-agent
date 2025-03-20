#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块 - 负责加载和管理翻译工具的配置
"""

import os
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


# 日志配置
def setup_logging():
    """设置日志记录"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        handlers=[logging.FileHandler("translator.log"), logging.StreamHandler()],
    )

    # 设置第三方库的日志级别
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.CRITICAL)
    logging.getLogger("httpx").setLevel(logging.CRITICAL)

    # 完全禁用某些模块的日志
    logging.getLogger("httpcore._trace").disabled = True

    return logging.getLogger("translator")


# 创建全局日志对象
logger = setup_logging()


class Config:
    """应用配置类"""

    def __init__(self):
        # API设置
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")

        # 模型设置
        self.model_name = os.getenv("MODEL_NAME", "deepseek-chat")
        self.max_tokens = int(os.getenv("MAX_TOKENS", "8192"))

        # 验证配置
        self._validate_config()

    def _validate_config(self):
        """验证配置的有效性"""
        if not self.api_key:
            logger.warning("未设置API密钥(DEEPSEEK_API_KEY)，翻译功能将无法使用")


# 创建默认配置对象
config = Config()
