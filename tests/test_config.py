#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置模块单元测试
"""

import os
from unittest.mock import patch

# 导入测试目标
from src.translator.config import Config


class TestConfig:
    """配置类测试"""

    def test_config_initialization(self):
        """测试配置初始化默认值"""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            # 测试默认值设置正确
            assert config.model_name == "deepseek-chat"
            assert config.max_tokens == 8192

    def test_config_from_env(self, tmpdir):
        """测试从环境变量读取配置"""
        test_env = {
            "DEEPSEEK_API_KEY": "test-api-key",
            "MODEL_NAME": "test-model",
            "MAX_TOKENS": "1024",
        }

        with patch.dict(os.environ, test_env, clear=True):
            config = Config()
            # 测试环境变量被正确读取
            assert config.api_key == "test-api-key"
            assert config.model_name == "test-model"
            assert config.max_tokens == 1024

    def test_warning_for_missing_api_key(self, caplog):
        """测试缺少API密钥时发出警告"""
        with patch.dict(os.environ, {}, clear=True):
            Config()
            # 验证日志中有警告消息
            assert any("未设置API密钥" in record.message for record in caplog.records)
