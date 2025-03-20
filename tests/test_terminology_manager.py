#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
术语管理模块单元测试
"""

import os
import pytest
import pandas as pd
from unittest.mock import patch

# 导入测试目标
from src.translator.terminology_manager import TerminologyManager


class TestTerminologyManager:
    """术语管理器测试"""

    @pytest.fixture
    def sample_terminology_file(self, tmpdir):
        """创建一个样本术语表文件"""
        file_path = os.path.join(tmpdir, "test_terminology.csv")
        df = pd.DataFrame(
            {
                "english": ["data structure", "algorithm", "binary search tree"],
                "chinese": ["数据结构", "算法", "二叉搜索树"],
            }
        )
        df.to_csv(file_path, index=True)
        return file_path

    def test_init_with_file(self, sample_terminology_file):
        """测试加载指定的术语表文件"""
        manager = TerminologyManager(sample_terminology_file)

        # 验证术语已正确加载
        assert len(manager.terminology) == 3
        assert manager.terminology["data structure"] == "数据结构"
        assert manager.terminology["algorithm"] == "算法"
        assert manager.terminology["binary search tree"] == "二叉搜索树"

    def test_init_without_file(self):
        """测试不存在的术语表文件"""
        with patch("os.path.exists", return_value=False):
            manager = TerminologyManager("nonexistent.csv")
            assert len(manager.terminology) == 0

    def test_save_terminology(self, tmpdir):
        """测试保存术语表"""
        file_path = os.path.join(tmpdir, "output_terminology.csv")
        manager = TerminologyManager(file_path)

        # 添加术语
        manager.terminology = {
            "data structure": "数据结构",
            "algorithm": "算法",
            "empty term": "",  # 这个应该被过滤掉
        }

        # 保存
        manager.save_terminology()

        # 验证文件被创建并且内容正确
        assert os.path.exists(file_path)
        df = pd.read_csv(file_path)
        assert len(df) == 2  # 空术语被过滤
        assert set(df["english"].tolist()) == {"data structure", "algorithm"}
        assert set(df["chinese"].tolist()) == {"数据结构", "算法"}

    def test_extract_terms(self, mock_terminology_response, monkeypatch):
        """测试术语提取"""

        # 模拟API调用返回固定结果
        def mock_api_extract_terms(*args, **kwargs):
            return mock_terminology_response

        # 应用模拟
        from src.translator.api_client import api_client

        monkeypatch.setattr(api_client, "extract_terms", mock_api_extract_terms)

        # 测试术语提取
        manager = TerminologyManager("nonexistent.csv")
        terms = manager.extract_terms(
            "Sample text with data structure and binary search tree"
        )

        # 验证术语提取结果
        assert isinstance(terms, list)
        assert len(terms) == 2
        assert ("data structure", "数据结构") in terms
        assert ("binary search tree", "二叉搜索树") in terms

    def test_find_relevant_terms(self):
        """测试应用术语表替换"""
        manager = TerminologyManager("nonexistent.csv")
        manager.terminology = {
            "data structure": "数据结构",
            "binary search tree": "二叉搜索树",
            "algorithm": "算法",
        }

        text = "This is a data structure and a binary search tree. We use algorithms to process them."
        result = manager.find_relevant_terms(text)

        # 验证替换结果
        assert ("binary search tree", "二叉搜索树") in result
        assert ("data structure", "数据结构") in result
        assert ("algorithm", "算法") in result

    def test_get_terminology_string(self):
        """测试术语表字符串生成"""
        manager = TerminologyManager("nonexistent.csv")

        # 获取术语表字符串
        result = manager.get_terminology_string(
            [("data structure", "数据结构"), ("algorithm", "算法")]
        )

        # 验证结果
        assert "data structure: 数据结构" in result
        assert "algorithm: 算法" in result

    def test_get_terminology_string_with_terms(self):
        """测试使用指定术语生成术语表字符串"""
        manager = TerminologyManager("nonexistent.csv")

        # 指定术语列表
        terms = [("term1", "Term 1"), ("term2", "Term 2")]
        result = manager.get_terminology_string(terms)

        # 验证结果
        assert "term1: Term 1" in result
        assert "term2: Term 2" in result
