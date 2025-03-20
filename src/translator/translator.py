#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
翻译核心模块 - 实现翻译流程
"""

from .config import logger
from .models import TranslationUnit
from .terminology_manager import TerminologyManager
from .api_client import api_client
from .utils import is_code_block


class Translator:
    """翻译器，实现多步翻译流程"""

    def __init__(self, terminology_manager: TerminologyManager):
        """初始化翻译器
        Args:
            terminology_manager: 术语管理器实例
        """
        self.terminology_manager = terminology_manager

    def translate_unit(self, unit: TranslationUnit) -> TranslationUnit:
        """
        对翻译单元执行多步翻译流程

        步骤:
        1. 使用术语表翻译原文
        2. 检查翻译并提供修改建议
        3. 润色最终翻译

        Args:
            unit: 要翻译的单元

        Returns:
            翻译后的单元
        """
        # 如果是代码块，不进行翻译
        if is_code_block(unit):
            unit.translation = unit.original_text
            unit.polished_translation = unit.original_text
            return unit

        # 1. 使用术语表翻译原文
        self._translate_text(unit)

        # 2. 检查翻译并提供修改建议
        self._review_translation(unit)

        # 3. 最终润色
        self._polish_translation(unit)

        return unit

    def _extract_terms(self, unit: TranslationUnit) -> TranslationUnit:
        """
        提取并保存术语

        Args:
            unit: 翻译单元

        Returns:
            更新后的翻译单元
        """
        # 提取术语
        unit.technical_terms = self.terminology_manager.extract_terms(
            unit.original_text
        )
        return unit

    def _translate_text(self, unit: TranslationUnit) -> TranslationUnit:
        """
        翻译文本

        Args:
            unit: 翻译单元

        Returns:
            包含翻译结果的翻译单元
        """
        # 查找文本中出现的相关术语，而不是使用全量术语表
        unit.technical_terms = self.terminology_manager.find_relevant_terms(
            unit.original_text
        )

        # 只有当找到相关术语时，才将术语信息添加到请求中
        terminology_str = ""
        if unit.technical_terms:
            # 准备术语表字符串，只包含相关术语
            terminology_str = self.terminology_manager.get_terminology_string(
                unit.technical_terms
            )
            logger.info(f"翻译请求中包含 {len(unit.technical_terms)} 个术语")
        else:
            logger.info("翻译请求中不包含术语信息")

        # 调用API翻译
        unit.translation = api_client.translate_text(
            unit.original_text, terminology_str
        )
        return unit

    def _review_translation(self, unit: TranslationUnit) -> None:
        """
        审查翻译质量

        Args:
            unit: 翻译单元

        Returns:
            包含审查建议的翻译单元
        """
        # 如果翻译失败或为空，跳过审查
        if not unit.translation or unit.translation == unit.original_text:
            unit.suggestions = ""
            return unit

        # 只有当有术语时，才将术语信息添加到请求中
        terminology_str = ""
        if unit.technical_terms:
            terminology_str = self.terminology_manager.get_terminology_string(
                unit.technical_terms
            )

        # 调用API审查翻译
        unit.suggestions = api_client.review_translation(
            unit.original_text, unit.translation, terminology_str
        )
        return unit

    def _polish_translation(self, unit: TranslationUnit) -> None:
        """
        润色翻译

        Args:
            unit: 翻译单元

        Returns:
            包含润色后翻译的翻译单元
        """
        # 如果翻译失败或为空，跳过润色
        if not unit.translation:
            unit.polished_translation = ""
            logger.info("无法润色翻译，因为翻译为空")
            return unit

        # 如果翻译与原文相同，可能是代码块等不需要翻译的内容
        if unit.translation == unit.original_text:
            unit.polished_translation = unit.translation
            logger.info("翻译与原文相同，跳过润色")
            return unit

        # 只有当有术语时，才将术语信息添加到请求中
        terminology_str = ""
        if unit.technical_terms:
            terminology_str = self.terminology_manager.get_terminology_string(
                unit.technical_terms
            )

        # 调用API润色翻译
        unit.polished_translation = api_client.polish_translation(
            unit.original_text, unit.translation, unit.suggestions, terminology_str
        )
        return unit
