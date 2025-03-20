#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据模型模块 - 定义翻译工具使用的数据结构
"""

from typing import List, Tuple
from dataclasses import dataclass, field


@dataclass
class TranslationUnit:
    """
    翻译单元，表示要翻译的段落及其相关信息

    翻译工作流程中的基本单位，对应Markdown中的一个段落或区块。
    包含原始文本、识别的术语、以及各阶段翻译结果。
    """

    original_text: str = ""
    translation: str = ""
    polished_translation: str = ""
    technical_terms: List[Tuple[str, str]] = field(default_factory=list)
    suggestions: str = ""


@dataclass
class TranslationContext:
    """
    翻译上下文，包含翻译过程中需要的状态信息

    简化版的上下文对象，仅用于追踪当前处理进度，不再保存中断恢复状态信息。
    """

    current_file: str = ""  # 当前正在处理的文件
    current_unit_index: int = -1  # 当前处理的单元索引
    total_units: int = 0  # 总单元数

    def update_progress(self, file: str = None, index: int = None, total: int = None):
        """更新进度信息"""
        if file is not None:
            self.current_file = file
        if index is not None:
            self.current_unit_index = index
        if total is not None:
            self.total_units = total

    def clear(self):
        """清除上下文信息"""
        self.current_file = ""
        self.current_unit_index = -1
        self.total_units = 0


@dataclass
class TranslationResult:
    """
    翻译结果，包含整体翻译的结果信息

    用于记录翻译过程的结果，如成功/失败文件、输出路径等。
    """

    success: bool = True  # 是否成功
    output_file: str = ""  # 输出文件路径
    error_message: str = ""  # 错误信息
