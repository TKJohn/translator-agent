#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
处理器模块 - 管理整个翻译过程
"""

import os
import concurrent.futures
from tqdm import tqdm
from typing import List, Dict, Tuple

from .config import logger
from .models import TranslationUnit, TranslationContext, TranslationResult
from .terminology_manager import TerminologyManager
from .translator import Translator
from .utils import is_code_block


class Processor:
    """处理器，处理整个工作流"""

    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        terminology_manager: TerminologyManager,
        translator: Translator,
    ):
        """
        初始化处理器

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            terminology_manager: 术语管理器
            translator: 翻译器
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.context = TranslationContext()
        self.terminology_manager = terminology_manager
        self.translator = translator
        self.min_unit_length = 4000  # 最小单元长度阈值，小于此长度的单元可能会被合并

    def translate_file(self, markdown_file: str) -> TranslationResult:
        """
        处理单个Markdown文件

        Args:
            markdown_file: Markdown文件路径

        Returns:
            处理结果
        """
        logger.info(f"处理文件: {markdown_file}")
        result = TranslationResult()

        try:
            # 设置当前处理的文件
            self.context.update_progress(file=markdown_file)

            # 读取Markdown文件
            markdown_content = self._read_markdown_file(markdown_file)

            # 提取翻译单元
            units = self._extract_translation_units(markdown_content)
            self.context.update_progress(total=len(units))
            logger.info(f"提取了 {len(units)} 个翻译单元")

            # 初始化输出文件
            output_file = self._get_output_path(markdown_file)
            result.output_file = output_file

            # 清空输出文件内容
            self._initialize_output_file(output_file)

            # 翻译每个单元，并在每个单元完成后保存结果
            self._process_translation_units(units, output_file)

            # 清除当前处理状态
            self.context.clear()

            logger.info(f"翻译完成，结果保存到: {output_file}")
            return result

        except Exception as e:
            logger.error(f"处理文件时出错: {e}")
            result.success = False
            result.error_message = str(e)
            return result

    def _read_markdown_file(self, file_path: str) -> str:
        """
        读取Markdown文件内容

        Args:
            file_path: 文件路径

        Returns:
            Markdown内容
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试使用其他编码
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()

    def _initialize_output_file(self, output_file: str) -> None:
        """
        初始化输出文件

        Args:
            output_file: 输出文件路径
        """
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # 清空输出文件内容
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("")

    def _process_translation_units(
        self, units: List[TranslationUnit], output_file: str
    ) -> None:
        """
        处理翻译单元

        Args:
            units: 翻译单元列表
            output_file: 输出文件路径
        """
        # 存储翻译结果的字典，键为原始索引，值为翻译后的内容
        results: Dict[int, str] = {}

        # 定义处理单个翻译单元的函数
        def process_unit(index: int, unit: TranslationUnit) -> Tuple[int, str]:
            # 翻译当前单元
            translated_unit = self.translator.translate_unit(unit)
            # 返回索引和翻译结果
            return index, translated_unit.polished_translation

        # 使用线程池并行处理翻译任务
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # 提交所有翻译任务到线程池
            future_to_index = {
                executor.submit(process_unit, i, unit): i
                for i, unit in enumerate(units)
            }

            # 使用tqdm显示进度
            for future in tqdm(
                concurrent.futures.as_completed(future_to_index),
                total=len(units),
                desc="翻译进度",
            ):
                index, translation = future.result()
                # 存储结果，保留原始索引
                results[index] = translation
                # 更新当前处理的单元索引（虽然是并行的，但仍然记录进度）
                self.context.update_progress(index=index)
                # 打印进度
                completed = len(results)
                progress = completed / len(units) * 100
                logger.info(
                    f"已完成 {completed}/{len(units)} 个翻译单元 ({progress:.1f}%)"
                )

        # 按原始顺序写入结果
        for i in range(len(units)):
            self._append_to_output_file(output_file, results[i])

        logger.info("所有翻译单元处理完成，已按原始顺序写入结果文件。")

    def _append_to_output_file(self, output_file: str, content: str) -> None:
        """
        追加内容到输出文件

        Args:
            output_file: 输出文件路径
            content: 要追加的内容
        """
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(content + "\n\n")

    def _get_output_path(self, input_file: str) -> str:
        """
        根据输入文件路径生成输出文件路径

        Args:
            input_file: 输入文件路径

        Returns:
            输出文件路径
        """
        # 获取相对路径
        try:
            relative_path = os.path.relpath(input_file, self.input_dir)
        except ValueError:
            # 如果输入文件不在输入目录下，使用文件名
            relative_path = os.path.basename(input_file)

        # 构建输出路径
        output_path = os.path.join(self.output_dir, relative_path)

        # 确保扩展名为.md
        if not output_path.lower().endswith(".md"):
            output_path = os.path.splitext(output_path)[0] + ".md"

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        return output_path

    def translate_directory(self) -> tuple:
        """
        处理整个目录下的Markdown文件

        Returns:
            (成功处理的文件数, 失败的文件列表)
        """

        # 查找所有Markdown文件
        markdown_files = self._find_markdown_files()

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

        # 翻译文件
        success_count, failed_files = self._translate_markdown_files(markdown_files)

        # 记录最终结果
        self._record_final_results(success_count, failed_files, markdown_files)

        return success_count, failed_files

    def _find_markdown_files(self) -> List[str]:
        """
        查找所有需要处理的Markdown文件

        Returns:
            文件路径列表
        """
        markdown_files = []

        # 遍历输入目录
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                # 只处理Markdown文件
                if file.lower().endswith(".md"):
                    file_path = os.path.join(root, file)
                    markdown_files.append(file_path)

        return markdown_files

    def _translate_markdown_files(self, markdown_files: List[str]) -> tuple:
        """
        翻译多个Markdown文件

        Args:
            markdown_files: Markdown文件路径列表

        Returns:
            (成功处理的文件数, 失败的文件列表)
        """
        success_count = 0
        failed_files = []

        for i, markdown_file in enumerate(markdown_files):
            try:
                logger.info(
                    f"翻译文件 [{i + 1}/{len(markdown_files)}]: {markdown_file}"
                )

                # 翻译文件
                result = self.translate_file(markdown_file)

                if result.success:
                    success_count += 1
                else:
                    failed_files.append((markdown_file, result.error_message))
                    logger.error(f"翻译文件失败: {result.error_message}")

            except Exception as e:
                failed_files.append((markdown_file, str(e)))
                logger.error(f"翻译文件 {markdown_file} 时发生错误: {e}")

                # 继续处理下一个文件
                continue

        return success_count, failed_files

    def _record_final_results(
        self, success_count: int, failed_files: List[tuple], markdown_files: List[str]
    ) -> None:
        """
        记录最终处理结果

        Args:
            success_count: 成功处理的文件数
            failed_files: 失败的文件列表
            markdown_files: 全部Markdown文件列表
        """
        if markdown_files:
            logger.info(
                f"处理完成: 成功 {success_count}/{len(markdown_files)}, 失败 {len(failed_files)}/{len(markdown_files)}"
            )
            if failed_files:
                logger.warning("失败文件列表:")
                for file_path, error in failed_files:
                    logger.warning(f"  - {file_path}: {error}")
        else:
            logger.warning("没有找到任何Markdown文件")

    def extract_terminology(self, input_path: str) -> None:
        """
        术语抽取模式：从输入文件中提取术语并保存到术语表
        """
        # 查找所有Markdown文件
        markdown_files = (
            self._find_markdown_files() if os.path.isdir(input_path) else [input_path]
        )

        for markdown_file in markdown_files:
            logger.info(f"提取术语: {markdown_file}")
            try:
                # 读取Markdown文件
                markdown_content = self._read_markdown_file(markdown_file)

                # 提取翻译单元
                units = self._extract_translation_units(markdown_content)

                # 提取术语
                for unit in units:
                    if is_code_block(unit):
                        logger.info(f"跳过代码块:{unit.original_text}")
                        continue

                    self.terminology_manager.extract_terms(unit.original_text)

                    # 保存术语表
                    self.terminology_manager.save_terminology()

            except Exception as e:
                logger.error(f"提取术语时出错: {e}")
                continue

    def _extract_translation_units(
        self, markdown_content: str
    ) -> List[TranslationUnit]:
        """
        从Markdown内容中提取翻译单元，并进行分片

        按照换行符进行分片
        代码块单独成为一片
        合并片直到长度大于阈值
        合并后长度小于阈值的单元可能会被合并

        Args:
            markdown_content: 完整的Markdown内容

        Returns:
            翻译单元列表
        """

        # 记录原始Markdown内容
        logger.info(f"原始Markdown内容:\n{markdown_content}")

        # 进行分片
        units = []
        current_unit = TranslationUnit()
        in_code_block = False
        for line in markdown_content.splitlines():
            if line.find("```") >= 0:
                if in_code_block:
                    #  结束代码块
                    current_unit.original_text += line
                    units.append(current_unit)
                    in_code_block = not in_code_block
                    current_unit = TranslationUnit()
                else:
                    # 遇到代码块
                    if current_unit.original_text:
                        # 提交当前单元到列表
                        units.append(current_unit)

                    # 开始新的代码块
                    in_code_block = not in_code_block
                    current_unit = TranslationUnit()
                    current_unit.original_text += line + "\n"
            else:
                if len(current_unit.original_text) + len(line) > self.min_unit_length:
                    units.append(current_unit)
                    current_unit = TranslationUnit()
                current_unit.original_text += line + "\n"
        if current_unit.original_text:
            units.append(current_unit)

        # 记录提取的翻译单元
        logger.info(f"提取的翻译单元:\n{units}")

        return units
