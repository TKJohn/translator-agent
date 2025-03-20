#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据模型模块单元测试
"""

# 导入测试目标
from src.translator.models import TranslationUnit, TranslationContext, TranslationResult


class TestTranslationUnit:
    """翻译单元测试"""

    def test_translation_unit_initialization(self):
        """测试翻译单元初始化"""
        unit = TranslationUnit(original_text="This is a test")

        assert unit.original_text == "This is a test"
        assert unit.translation == ""
        assert unit.suggestions == ""
        assert unit.polished_translation == ""
        assert unit.technical_terms == []

    def test_translation_unit_with_params(self):
        """测试带参数的翻译单元初始化"""
        terms = [("test", "测试")]
        unit = TranslationUnit(
            original_text="This is a test",
            technical_terms=terms,
            translation="这是一个测试",
        )

        assert unit.translation == "这是一个测试"
        assert unit.technical_terms == terms


class TestTranslationContext:
    """翻译上下文测试"""

    def test_translation_context_initialization(self):
        """测试翻译上下文初始化"""
        context = TranslationContext()

        assert context.current_file == ""
        assert context.current_unit_index == -1
        assert context.total_units == 0

    def test_update_progress(self):
        """测试更新进度功能"""
        context = TranslationContext()
        context.update_progress(file="test.html", index=5, total=10)

        assert context.current_file == "test.html"
        assert context.current_unit_index == 5
        assert context.total_units == 10

        # 测试部分更新
        context.update_progress(index=6)

    def test_clear(self):
        """测试清除功能"""
        context = TranslationContext()
        context.update_progress(file="test.html", index=5, total=10)
        context.clear()

        assert context.current_file == ""
        assert context.current_unit_index == -1
        assert context.total_units == 0


class TestTranslationResult:
    """翻译结果测试"""

    def test_translation_result_defaults(self):
        """测试翻译结果默认值"""
        result = TranslationResult()

        assert result.success is True
        assert result.output_file == ""
        assert result.error_message == ""

    def test_translation_result_with_params(self):
        """测试带参数的翻译结果初始化"""
        result = TranslationResult(
            success=False, output_file="test_output.md", error_message="Test error"
        )

        assert result.success is False
        assert result.output_file == "test_output.md"
        assert result.error_message == "Test error"
