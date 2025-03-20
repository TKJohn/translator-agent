#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试配置和共享测试夹具
"""

import os
import sys
import pytest

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 测试数据目录
TEST_DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_data"))
TEST_INPUT_DIR = os.path.join(TEST_DATA_DIR, "input")
TEST_OUTPUT_DIR = os.path.join(TEST_DATA_DIR, "output")
TEST_TERMINOLOGY_FILE = os.path.join(TEST_DATA_DIR, "terminology.csv")

# 测试HTML样本路径
TEST_HTML_SAMPLE = os.path.join(TEST_INPUT_DIR, "sample.html")


@pytest.fixture
def sample_html_path():
    """返回测试HTML样本的路径"""
    return TEST_HTML_SAMPLE


@pytest.fixture
def sample_html_content():
    """返回测试HTML样本的内容"""
    with open(TEST_HTML_SAMPLE, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def test_terminology_path():
    """返回测试术语表的路径"""
    return TEST_TERMINOLOGY_FILE


@pytest.fixture
def test_input_dir():
    """返回测试输入目录的路径"""
    return TEST_INPUT_DIR


@pytest.fixture
def test_output_dir():
    """返回测试输出目录的路径"""
    return TEST_OUTPUT_DIR


@pytest.fixture
def mock_api_response():
    """模拟API响应"""
    return {"choices": [{"message": {"content": "这是一个模拟的API响应内容"}}]}


@pytest.fixture
def mock_terminology_response():
    """模拟术语提取API响应"""
    return [
        {"english": "data structure", "chinese": "数据结构"},
        {"english": "binary search tree", "chinese": "二叉搜索树"},
    ]


@pytest.fixture
def mock_translation_response():
    """模拟翻译API响应"""
    return "这是一个数据结构的介绍。数据结构是一种在计算机中组织和存储数据的方式，以便我们可以更高效地对数据执行操作。数据结构几乎用于每个程序或软件系统中。"
