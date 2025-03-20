#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具函数模块单元测试
"""

import os
import sys
import time
from io import StringIO
from datetime import datetime

# 导入测试目标
from src.translator.utils import (
    get_absolute_path,
    ensure_dir_exists,
    get_file_extension,
    format_timestamp,
    print_progress,
)


class TestUtils:
    """工具函数测试"""

    def test_get_absolute_path(self):
        """测试获取绝对路径"""
        # 测试相对路径
        rel_path = "test/path"
        abs_path = get_absolute_path(rel_path)
        assert os.path.isabs(abs_path)
        assert rel_path in abs_path

        # 测试绝对路径不变
        orig_abs_path = os.path.abspath("/test/absolute/path")
        result_abs_path = get_absolute_path(orig_abs_path)
        assert orig_abs_path == result_abs_path

    def test_ensure_dir_exists(self, tmpdir):
        """测试确保目录存在"""
        test_dir = os.path.join(tmpdir, "test_dir")

        # 确认目录不存在
        assert not os.path.exists(test_dir)

        # 调用测试函数
        ensure_dir_exists(test_dir)

        # 验证目录被创建
        assert os.path.exists(test_dir)
        assert os.path.isdir(test_dir)

        # 再次调用，确保不会出错
        ensure_dir_exists(test_dir)
        assert os.path.exists(test_dir)

    def test_get_file_extension(self):
        """测试获取文件扩展名"""
        # 测试常见扩展名
        assert get_file_extension("test.txt") == "txt"
        assert get_file_extension("path/to/file.html") == "html"
        assert get_file_extension("no_extension") == ""
        assert get_file_extension(".hidden") == "hidden"
        assert get_file_extension("file.with.multiple.dots.md") == "md"
        assert get_file_extension("FILE.TXT") == "txt"  # 测试大写转小写

    def test_format_timestamp(self):
        """测试时间戳格式化"""
        # 测试指定时间戳
        timestamp = datetime(2023, 1, 1, 12, 0, 0).timestamp()
        formatted = format_timestamp(timestamp)
        assert formatted == "2023-01-01 12:00:00"

        # 测试当前时间（只能近似测试）
        now = time.time()
        formatted = format_timestamp()
        now_formatted = datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M")
        assert now_formatted in formatted

    def test_print_progress(self):
        """测试打印进度条"""
        # 替换stdout以捕获输出
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            # 测试打印进度
            print_progress(50, 100, prefix="Progress:", suffix="Complete", length=20)
            output = captured_output.getvalue()

            # 验证输出
            assert "Progress:" in output
            assert "50.0%" in output
            assert "Complete" in output
            assert "|" in output  # 进度条边界

            # 测试进度完成时的换行
            captured_output.truncate(0)
            captured_output.seek(0)

            print_progress(100, 100)
            output = captured_output.getvalue()
            assert output.endswith("\n")

        finally:
            # 恢复stdout
            sys.stdout = sys.__stdout__
