#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
术语管理模块 - 处理术语的提取、存储和应用
"""

import os
import re
import pandas as pd
from typing import Dict, List, Tuple

from .config import logger
from .api_client import api_client


class TerminologyManager:
    """术语管理器，负责术语的提取、存储和应用"""

    def __init__(self, terminology_file: str):
        """
        初始化术语管理器

        Args:
            terminology_file: 术语表文件路径，如不指定则使用配置中的默认路径
        """
        self.terminology_file = terminology_file
        self.terminology: Dict[str, str] = {}  # 英文 -> 中文
        self._load_terminology()

    def _load_terminology(self) -> None:
        """从CSV文件加载现有术语表"""
        try:
            if os.path.exists(self.terminology_file):
                df = pd.read_csv(self.terminology_file)
                # 将英文术语转为小写，以忽略大小写差异
                self.terminology = {
                    eng.lower(): chn for eng, chn in zip(df["english"], df["chinese"])
                }
                logger.info(f"已加载 {len(self.terminology)} 个术语")
        except Exception as e:
            logger.error(f"加载术语表时出错: {e}")

    def save_terminology(self) -> None:
        """保存术语表到CSV文件"""
        try:
            # 过滤出有翻译的术语
            valid_terms = {k: v for k, v in self.terminology.items() if v and v.strip()}
            sorted_terms = dict(sorted(valid_terms.items(), key=lambda x: x[0]))

            df = pd.DataFrame(
                {
                    "english": list(sorted_terms.keys()),
                    "chinese": list(sorted_terms.values()),
                }
            )

            # 确保目录存在
            os.makedirs(os.path.dirname(self.terminology_file), exist_ok=True)

            # 保存到CSV
            df.to_csv(self.terminology_file, index=False)
            logger.info(
                f"术语表已保存到 {self.terminology_file}，共 {len(valid_terms)} 个术语"
            )
        except Exception as e:
            logger.error(f"保存术语表时出错: {e}")

    def extract_terms(self, text: str) -> List[Tuple[str, str]]:
        """
        从文本中提取技术术语

        Args:
            text: 要分析的文本

        Returns:
            提取的术语列表 [(英文术语, 中文翻译), ...]
        """
        # 如果文本太短，直接返回空列表
        if len(text) < 30:
            logger.info("文本太短，跳过术语提取")
            return []

        # 系统提示词
        system_prompt = f"""
<角色>你是一位计算机科学领域的术语专家，精通中英双语术语标准化翻译
<任务>请从以下英文原文中提取计算机专业术语，并生成中英对照表
<要求>
优先参考《计算机科学技术名词》第三版
涉及编程语言术语时参照官方中文文档
新兴技术术语采用行业公认翻译
英文使用全小写单数形式

<输出>  英文:中文

<输入文本>
{text}

<示例>
Text Generation:文本生成
Token:Token
Prompt:提示词
Meta Prompting:元提示
full-stack:全栈
"""

        try:
            # 调用API提取术语
            try:
                terms_list = api_client.extract_terms(text, system_prompt)
            except Exception as e:
                logger.warning(f"调用术语提取API失败: {str(e)}")
                return []

            # 更新术语表
            new_terms = []
            for term in terms_list:
                if not isinstance(term, dict):
                    logger.warning(f"术语格式不正确，不是字典: {term}")
                    continue

                if "english" not in term or "chinese" not in term:
                    logger.warning(f"术语缺少必要字段: {term}")
                    continue

                english = (
                    term["english"].strip() if isinstance(term["english"], str) else ""
                )
                chinese = (
                    term["chinese"].strip() if isinstance(term["chinese"], str) else ""
                )

                if not english:
                    logger.info("跳过空术语")
                    continue

                # 将英文术语转为小写，以忽略大小写差异
                english_lower = english.lower()

                # 如果术语已存在且有翻译，使用已有的
                if (
                    english_lower in self.terminology
                    and self.terminology[english_lower]
                ):
                    chinese = self.terminology[english_lower]

                # 更新术语表
                if english_lower and (english_lower not in self.terminology):
                    self.terminology[english_lower] = chinese
                    if chinese:  # 只添加有翻译的术语到结果中
                        new_terms.append(
                            (english, chinese)
                        )  # 保留原始大小写形式用于显示

            return new_terms

        except Exception as e:
            logger.warning(f"提取术语时出错: {str(e)}")
            return []

    def get_terminology_string(self, terms: List[Tuple[str, str]] = None) -> str:
        """
        将术语表转换为字符串格式

        Args:
            terms: 术语列表，如不指定则忽略术语

        Returns:
            术语表字符串，每行一个术语
        """
        if terms:
            # 使用指定的术语列表
            return "\n".join([f"{eng}: {chn}" for eng, chn in terms if chn])
        else:
            return ""

    def find_relevant_terms(self, text: str) -> List[Tuple[str, str]]:
        """
        从文本中识别已存在于术语表中的术语

        Args:
            text: 要分析的文本

        Returns:
            文本中出现的术语列表 [(英文术语, 中文翻译), ...]
        """
        if not text or len(text) < 10:
            logger.info("文本太短，跳过术语匹配")
            return []

        # 检查术语表是否为空
        if not self.terminology:
            logger.info("术语表为空，跳过术语匹配")
            return []

        # 按照术语长度排序，确保先匹配最长的术语
        sorted_terms = sorted(
            self.terminology.items(), key=lambda x: len(x[0]), reverse=True
        )
        found_terms = []

        for eng, chn in sorted_terms:
            if not eng or not chn:  # 跳过没有翻译的术语
                continue

            # 检查基本形式
            pattern = r"\b" + re.escape(eng) + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                found_terms.append((eng, chn))
                continue

            # 检查可能的复数形式
            if eng.endswith(("s", "x", "z", "ch", "sh")):
                # 对于以s, x, z, ch, sh结尾的词，复数加es
                plural_pattern = r"\b" + re.escape(eng) + r"es\b"
            elif eng.endswith("y") and len(eng) > 1 and eng[-2] not in "aeiou":
                # 以辅音字母+y结尾的词，复数将y变为ies
                plural_pattern = r"\b" + re.escape(eng[:-1]) + r"ies\b"
            else:
                # 一般情况下直接加s
                plural_pattern = r"\b" + re.escape(eng) + r"s\b"

            # 对于已经是复数形式的术语，不做额外处理
            if not re.search(plural_pattern, eng, re.IGNORECASE) and re.search(
                plural_pattern, text, re.IGNORECASE
            ):
                found_terms.append((eng, chn))

        logger.info(f"在文本中找到 {len(found_terms)} 个相关术语")
        return found_terms
