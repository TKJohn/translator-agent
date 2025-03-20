#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
术语提取功能单元测试
"""

import pytest
from unittest.mock import patch

# 导入测试目标
from src.translator.api_client import ApiClient


class TestExtractTerms:
    """术语提取功能测试"""

    @pytest.fixture
    def api_client(self):
        """返回API客户端实例"""
        return ApiClient()

    def test_extract_terms_normal(self, api_client):
        """测试正常情况下的术语提取"""
        # 模拟API响应
        mock_response = (
            "data structure: 数据结构\nbinary search tree: 二叉搜索树\nalgorithm: 算法"
        )

        with patch.object(api_client, "_call_api", return_value=mock_response):
            result = api_client.extract_terms("Sample text", "System prompt")

            # 验证返回结果
            assert len(result) == 3
            assert result[0] == {"english": "data structure", "chinese": "数据结构"}
            assert result[1] == {
                "english": "binary search tree",
                "chinese": "二叉搜索树",
            }
            assert result[2] == {"english": "algorithm", "chinese": "算法"}

    def test_extract_terms_empty_response(self, api_client):
        """测试空响应情况"""
        with patch.object(api_client, "_call_api", return_value=""):
            result = api_client.extract_terms("Sample text", "System prompt")

            # 验证返回空列表
            assert result == []

    def test_extract_terms_invalid_format(self, api_client):
        """测试格式错误的响应"""
        # 模拟格式错误的响应
        mock_response = "这不是正确的术语格式"

        with patch.object(api_client, "_call_api", return_value=mock_response):
            result = api_client.extract_terms("Sample text", "System prompt")

            # 验证返回空列表
            assert result == []

    def test_extract_terms_error_handling(self, api_client):
        """测试术语提取错误处理"""
        with patch.object(api_client, "_call_api", side_effect=Exception("API error")):
            result = api_client.extract_terms("Sample text", "System prompt")

            # 验证错误时返回空列表
            assert result == []

    def test_extract_terms_with_empty_english(self, api_client):
        """测试英文术语为空的情况"""
        # 模拟包含空英文术语的响应
        mock_response = "data structure: 数据结构\n: 空术语\nalgorithm: 算法\n"

        with patch.object(api_client, "_call_api", return_value=mock_response):
            result = api_client.extract_terms("Sample text", "System prompt")

            # 验证只返回非空英文术语
            assert len(result) == 2
            assert result[0] == {"english": "data structure", "chinese": "数据结构"}
            assert result[1] == {"english": "algorithm", "chinese": "算法"}

    def test_extract_terms_internal(self, api_client):
        """测试内部_extract_terms方法"""
        # 测试正常情况
        text = "data structure: 数据结构\nbinary search tree: 二叉搜索树"
        result = api_client._extract_terms(text)
        assert len(result) == 2
        assert result[0] == {"english": "data structure", "chinese": "数据结构"}

        # 测试空文本
        assert api_client._extract_terms("") == []

        # 测试格式错误的文本
        assert api_client._extract_terms("这不是正确的术语格式") == []

    def test_extract_terms_with_hyphen(self, api_client):
        """测试包含连字符的术语提取"""
        # 模拟包含连字符的术语响应
        mock_response = "object-oriented programming: 面向对象编程\nmodel-view-controller: 模型-视图-控制器"

        with patch.object(api_client, "_call_api", return_value=mock_response):
            result = api_client.extract_terms("Sample text", "System prompt")

            # 验证能正确提取包含连字符的术语
            assert len(result) == 2
            assert result[0] == {
                "english": "object-oriented programming",
                "chinese": "面向对象编程",
            }
            assert result[1] == {
                "english": "model-view-controller",
                "chinese": "模型-视图-控制器",
            }
