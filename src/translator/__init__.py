#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
翻译工具包 - 将HTML格式的英文技术文档翻译为Markdown格式的中文文档
"""

from .config import config, logger

__version__ = "1.0.0"
__author__ = "Translator Agent Team"

import os
import sys
import platform

logger.info("=" * 80)
logger.info(f"翻译工具初始化 v{__version__}")
logger.info(f"Python版本: {sys.version}")
logger.info(f"操作系统: {platform.platform()}")
logger.info(f"工作目录: {os.getcwd()}")
logger.info(f"API密钥是否设置: {'是' if config.api_key else '否'}")
logger.info(f"API基础URL: {config.api_base}")
logger.info(f"使用的chat模型: {config.chat_model_name}")
logger.info(f"使用的reasoner模型: {config.reasoner_model_name}")
logger.info(f"最大令牌数: {config.max_tokens}")
logger.info("=" * 80)
