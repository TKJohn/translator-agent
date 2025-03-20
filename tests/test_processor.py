#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试处理器模块 - 测试翻译过程管理功能
"""

import os
import pytest
from unittest.mock import Mock, patch, mock_open

from src.translator.processor import Processor
from src.translator.models import TranslationUnit, TranslationContext
from src.translator.terminology_manager import TerminologyManager
from src.translator.translator import Translator


@pytest.fixture
def mock_terminology_manager():
    """创建模拟术语管理器"""
    manager = Mock(spec=TerminologyManager)
    manager.extract_terms.return_value = [("term1", "术语1"), ("term2", "术语2")]
    manager.find_relevant_terms.return_value = [("term1", "术语1")]
    return manager


@pytest.fixture
def mock_translator():
    """创建模拟翻译器"""
    translator = Mock(spec=Translator)

    # 模拟翻译单元的行为
    def translate_unit_side_effect(unit):
        if unit.original_text.find("```") >= 0:
            # 代码块不翻译
            unit.translation = unit.original_text
            unit.polished_translation = unit.original_text
        else:
            # 普通文本翻译
            unit.translation = f"翻译: {unit.original_text}"
            unit.polished_translation = f"润色翻译: {unit.original_text}"
        return unit

    translator.translate_unit.side_effect = translate_unit_side_effect
    return translator


@pytest.fixture
def processor(mock_terminology_manager, mock_translator, tmp_path):
    """创建处理器实例"""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    return Processor(
        input_dir=str(input_dir),
        output_dir=str(output_dir),
        terminology_manager=mock_terminology_manager,
        translator=mock_translator,
    )


class TestProcessor:
    """测试处理器类"""

    def test_init(self, processor, mock_terminology_manager, mock_translator, tmp_path):
        """测试初始化"""
        assert processor.input_dir == str(tmp_path / "input")
        assert processor.output_dir == str(tmp_path / "output")
        assert processor.terminology_manager == mock_terminology_manager
        assert processor.translator == mock_translator
        assert isinstance(processor.context, TranslationContext)
        assert processor.min_unit_length == 4000

    def test_read_markdown_file(self, processor, tmp_path):
        """测试读取Markdown文件"""
        # 创建测试文件
        test_file = tmp_path / "input" / "test.md"
        test_content = "# Test\n\nThis is a test file."
        test_file.write_text(test_content)

        # 测试读取
        content = processor._read_markdown_file(str(test_file))
        assert content == test_content

    def test_read_markdown_file_with_encoding_error(self, processor):
        """测试读取编码错误的Markdown文件"""
        with patch(
            "builtins.open",
            side_effect=[
                UnicodeDecodeError("utf-8", b"\x80", 1, 2, "invalid start byte"),
                mock_open(read_data="fallback content")(),
            ],
        ) as m:
            content = processor._read_markdown_file("test.md")
            assert content == "fallback content"
            assert m.call_count == 2

    def test_initialize_output_file(self, processor, tmp_path):
        """测试初始化输出文件"""
        output_file = tmp_path / "output" / "subdir" / "test.md"
        processor._initialize_output_file(str(output_file))

        # 验证目录已创建
        assert os.path.exists(os.path.dirname(str(output_file)))
        # 验证文件已创建且为空
        assert os.path.exists(str(output_file))
        assert os.path.getsize(str(output_file)) == 0

    def test_append_to_output_file(self, processor, tmp_path):
        """测试追加内容到输出文件"""
        output_file = tmp_path / "output" / "test.md"
        output_file.parent.mkdir(exist_ok=True)
        output_file.write_text("")

        # 追加内容
        processor._append_to_output_file(str(output_file), "Test content")

        # 验证内容
        assert output_file.read_text() == "Test content\n\n"

        # 再次追加
        processor._append_to_output_file(str(output_file), "More content")
        assert output_file.read_text() == "Test content\n\nMore content\n\n"

    def test_get_output_path(self, processor, tmp_path):
        """测试获取输出路径"""
        # 测试正常情况
        input_file = str(tmp_path / "input" / "subdir" / "test.md")
        output_path = processor._get_output_path(input_file)
        expected_path = str(tmp_path / "output" / "subdir" / "test.md")
        assert output_path == expected_path

        # 测试非md扩展名
        input_file = str(tmp_path / "input" / "test.txt")
        output_path = processor._get_output_path(input_file)
        expected_path = str(tmp_path / "output" / "test.md")
        assert output_path == expected_path

    def test_extract_translation_units(self, processor):
        """测试提取翻译单元"""
        # 测试普通文本
        markdown_content = "# 标题\n\n这是一段普通文本。\n\n这是另一段文本。"
        units = processor._extract_translation_units(markdown_content)
        assert len(units) == 1
        assert (
            units[0].original_text
            == "# 标题\n\n这是一段普通文本。\n\n这是另一段文本。\n"
        )

        # 测试包含代码块的文本
        markdown_content = "# 标题\n\n```python\nprint('Hello')\n```\n\n这是普通文本。"
        units = processor._extract_translation_units(markdown_content)
        assert len(units) == 3
        assert "```python" in units[1].original_text
        assert "print('Hello')" in units[1].original_text
        assert "```" in units[1].original_text

        # 测试长文本分片
        long_text = "A" * 5000
        units = processor._extract_translation_units(long_text)
        assert len(units) > 1

    def test_translate_file(self, processor, tmp_path, mock_translator):
        """测试翻译文件"""
        # 创建测试文件
        input_file = tmp_path / "input" / "test.md"
        input_file.parent.mkdir(exist_ok=True)
        input_file.write_text("# Test\n\nThis is a test file.")

        # 执行翻译
        result = processor.translate_file(str(input_file))

        # 验证结果
        assert result.success
        assert os.path.exists(result.output_file)
        assert mock_translator.translate_unit.called

        # 验证输出文件内容
        output_content = open(result.output_file, "r").read()
        assert "润色翻译" in output_content

    def test_translate_file_error(self, processor, tmp_path):
        """测试翻译文件出错"""
        # 创建不存在的文件路径
        input_file = tmp_path / "input" / "nonexistent.md"

        # 执行翻译
        result = processor.translate_file(str(input_file))

        # 验证结果
        assert not result.success
        assert result.error_message != ""

    def test_find_markdown_files(self, processor, tmp_path):
        """测试查找Markdown文件"""
        # 创建测试文件
        (tmp_path / "input" / "test1.md").write_text("content")
        (tmp_path / "input" / "subdir").mkdir()
        (tmp_path / "input" / "subdir" / "test2.md").write_text("content")
        (tmp_path / "input" / "test.txt").write_text("content")  # 非md文件

        # 查找文件
        files = processor._find_markdown_files()

        # 验证结果
        assert len(files) == 2
        assert any(f.endswith("test1.md") for f in files)
        assert any(f.endswith("test2.md") for f in files)
        assert not any(f.endswith(".txt") for f in files)

    def test_translate_directory(self, processor, tmp_path, mock_translator):
        """测试翻译目录"""
        # 创建测试文件
        (tmp_path / "input" / "test1.md").write_text("content1")
        (tmp_path / "input" / "test2.md").write_text("content2")

        # 执行翻译
        success_count, failed_files = processor.translate_directory()

        # 验证结果
        assert success_count == 2
        assert len(failed_files) == 0
        assert os.path.exists(tmp_path / "output" / "test1.md")
        assert os.path.exists(tmp_path / "output" / "test2.md")

    def test_translate_directory_with_errors(
        self, processor, tmp_path, mock_translator
    ):
        """测试翻译目录时出现错误"""
        # 创建测试文件
        (tmp_path / "input" / "test1.md").write_text("content1")

        # 模拟翻译错误
        mock_translator.translate_unit.side_effect = Exception("模拟翻译错误")

        # 执行翻译
        success_count, failed_files = processor.translate_directory()

        # 验证结果
        assert success_count == 0
        assert len(failed_files) == 1

    def test_extract_terminology(self, processor, tmp_path, mock_terminology_manager):
        """测试术语提取"""
        # 创建测试文件
        input_file = tmp_path / "input" / "test.md"
        input_file.parent.mkdir(exist_ok=True)
        input_file.write_text("# Test\n\nThis is a test file with terms.")

        # 执行术语提取
        processor.extract_terminology(str(input_file))

        # 验证结果
        assert mock_terminology_manager.extract_terms.called
        assert mock_terminology_manager.save_terminology.called

    def test_process_translation_units(self, processor, tmp_path, mock_translator):
        """测试处理翻译单元"""
        # 创建测试单元和输出文件
        units = [
            TranslationUnit(original_text="Text 1"),
            TranslationUnit(original_text="Text 2"),
        ]
        output_file = tmp_path / "output" / "test.md"
        output_file.parent.mkdir(exist_ok=True)
        output_file.write_text("")

        # 执行处理
        processor._process_translation_units(units, str(output_file))

        # 验证结果
        assert mock_translator.translate_unit.call_count == 2
        assert output_file.exists()
        content = output_file.read_text()
        assert "润色翻译: Text 1" in content
        assert "润色翻译: Text 2" in content
