#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
工具函数模块 - 提供各种辅助功能
"""

import os
import sys
from datetime import datetime
from typing import Optional
from .models import TranslationUnit


def get_absolute_path(path: str) -> str:
    """
    获取绝对路径

    Args:
        path: 相对或绝对路径

    Returns:
        绝对路径
    """
    return os.path.abspath(os.path.expanduser(path))


def ensure_dir_exists(path: str) -> None:
    """
    确保目录存在

    Args:
        path: 目录路径
    """
    os.makedirs(path, exist_ok=True)


def get_file_extension(file_path: str) -> str:
    """
    获取文件扩展名

    Args:
        file_path: 文件路径

    Returns:
        文件扩展名（小写，不含点）
    """
    # 处理隐藏文件（以.开头的文件）
    basename = os.path.basename(file_path)
    if basename.startswith(".") and "." not in basename[1:]:
        return basename[1:].lower()

    return os.path.splitext(file_path)[1].lower()[1:]


def format_timestamp(timestamp: Optional[float] = None) -> str:
    """
    格式化时间戳

    Args:
        timestamp: 时间戳，默认为当前时间

    Returns:
        格式化的时间字符串 (yyyy-mm-dd HH:MM:SS)
    """
    if timestamp is None:
        timestamp = datetime.now().timestamp()
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def print_progress(
    current: int,
    total: int,
    prefix: str = "",
    suffix: str = "",
    decimals: int = 1,
    length: int = 50,
    fill: str = "█",
) -> None:
    """
    打印进度条

    Args:
        current: 当前进度
        total: 总数
        prefix: 前缀字符串
        suffix: 后缀字符串
        decimals: 百分比小数位数
        length: 进度条长度
        fill: 进度条填充字符
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (current / float(total)))
    filled_length = int(length * current // total)
    bar = fill * filled_length + "-" * (length - filled_length)
    sys.stdout.write(f"\r{prefix} |{bar}| {percent}% {suffix}")
    sys.stdout.flush()

    # 如果完成则打印换行
    if current == total:
        print()


def is_code_block(unit: TranslationUnit) -> bool:
    """
    判断是否是代码块

    Args:
        unit: 翻译单元

    Returns:
        是否是代码块
    """
    return unit.original_text.find("```") >= 0
