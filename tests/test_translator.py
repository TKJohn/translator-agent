#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
翻译模块单元测试
"""

import pytest
from unittest.mock import patch

# 导入测试目标
from src.translator.translator import Translator
from src.translator.models import TranslationUnit
from src.translator.terminology_manager import TerminologyManager


class TestTranslator:
    """翻译器测试"""

    @pytest.fixture
    def translator(self):
        """返回翻译器实例"""
        terminology_manager = TerminologyManager("nonexistent.csv")
        return Translator(terminology_manager)

    def test_translate_unit_code_block(self, translator):
        """测试代码块不进行翻译"""
        unit = TranslationUnit(original_text="```python\ndef test():\n    pass\n```")

        result = translator.translate_unit(unit)

        # 验证代码块不被翻译
        assert result.translation == unit.original_text
        assert result.polished_translation == unit.original_text

    def test_translate_unit_normal_text(self, translator):
        """测试正常文本翻译流程"""
        unit = TranslationUnit(original_text="This is a test paragraph.")

        # 模拟依赖的函数
        with patch.object(
            translator, "_translate_text", return_value=unit
        ) as mock_translate_text, patch.object(
            translator, "_polish_translation", return_value=unit
        ) as mock_polish:

            translator.translate_unit(unit)

            # 验证调用流程
            mock_translate_text.assert_called_once()
            mock_polish.assert_called_once()

    def test_translate_text(self, translator):
        """测试文本翻译"""
        unit = TranslationUnit(
            original_text="Data structure example",
            technical_terms=[("data structure", "数据结构")],
        )

        with patch(
            "src.translator.terminology_manager.TerminologyManager.get_terminology_string",
            return_value="data structure: 数据结构",
        ), patch(
            "src.translator.api_client.api_client.translate_text",
            return_value="数据结构示例",
        ):

            result = translator._translate_text(unit)

            # 验证翻译结果
            assert result.translation == "数据结构示例"

    def test_polish_translation_empty(self, translator):
        """测试空翻译不进行润色"""
        unit = TranslationUnit(original_text="Test", translation="")

        result = translator._polish_translation(unit)

        # 验证空翻译时跳过润色
        assert result is not None
        assert result.polished_translation == ""

    def test_polish_translation(self, translator):
        """测试翻译润色"""
        unit = TranslationUnit(
            original_text="Test",
            translation="测试",
            suggestions="可以更自然些",
            technical_terms=[],
        )

        with patch(
            "src.translator.terminology_manager.TerminologyManager.get_terminology_string",
            return_value="",
        ), patch(
            "src.translator.api_client.api_client.polish_translation",
            return_value="自然的测试",
        ):

            result = translator._polish_translation(unit)

            # 验证润色结果
            assert result.polished_translation == "自然的测试"
