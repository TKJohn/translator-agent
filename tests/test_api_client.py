#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API模块单元测试
"""

import pytest
from unittest.mock import patch, MagicMock

# 导入测试目标
from src.translator.api_client import ApiClient


class TestApiClient:
    """API客户端测试"""

    @pytest.fixture
    def api_client(self):
        """返回API客户端实例"""
        return ApiClient()

    def test_init(self, api_client):
        """测试API客户端初始化"""
        # 此测试主要是为了确保初始化不会抛出异常
        assert api_client is not None

    def test_translate_text(self, api_client):
        """测试文本翻译API调用"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "这是翻译后的文本"

        with patch(
            "openai.resources.chat.completions.Completions.create",
            return_value=mock_response,
        ):
            result = api_client.translate_text(
                "This is the text to translate", "terminology string"
            )

            # 验证返回结果
            assert result == "这是翻译后的文本"

    def test_translate_text_error_handling(self, api_client):
        """测试文本翻译错误处理"""
        original_text = "This is the text to translate"

        with patch(
            "openai.resources.chat.completions.Completions.create",
            side_effect=Exception("API error"),
        ):
            result = api_client.translate_text(original_text, "terminology")

            # 验证错误时返回原文
            assert result == original_text

    def test_polish_translation(self, api_client):
        """测试翻译润色API调用"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "润色后的文本"

        with patch(
            "openai.resources.chat.completions.Completions.create",
            return_value=mock_response,
        ):
            result = api_client.polish_translation(
                "Original text", "Translated text", "terminology string"
            )

            # 验证返回结果
            assert result == "润色后的文本"

    def test_polish_translation_error_handling(self, api_client):
        """测试翻译润色错误处理"""
        translation = "Translated text"

        with patch(
            "openai.resources.chat.completions.Completions.create",
            side_effect=Exception("API error"),
        ):
            result = api_client.polish_translation(
                "Original", translation, "terminology"
            )

            # 验证错误时返回原翻译
            assert result == translation

    def test_call_api(self, api_client):
        """测试底层API调用方法"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "API response"

        with patch(
            "openai.resources.chat.completions.Completions.create",
            return_value=mock_response,
        ) as mock_create:
            result = api_client._call_api("System prompt", "User prompt", 0.5)

            # 验证返回结果
            assert result == "API response"

            # 验证API调用参数
            mock_create.assert_called_once()
            args, kwargs = mock_create.call_args
            assert kwargs["temperature"] == 0.3

    def test_call_api_error_handling(self, api_client):
        """测试底层API调用错误处理"""
        with patch(
            "openai.resources.chat.completions.Completions.create",
            side_effect=Exception("API error"),
        ):
            with pytest.raises(Exception) as excinfo:
                api_client._call_api("model", "System prompt", "User prompt")

            # 验证异常被抛出
            assert "API error" in str(excinfo.value)
