#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API模块 - 封装所有与外部API的交互
"""

import re
import time
import openai
from typing import List, Dict
from .config import config, logger


class ApiClient:
    """API客户端，封装与DeepSeek API的交互"""

    def __init__(self):
        """初始化API客户端"""
        import openai

        # 配置超时和重试设置
        self.timeout = 180.0  # 秒
        self.max_retries = 3

        # 记录超时和重试设置
        logger.info(f"配置API请求超时: {self.timeout}秒")
        logger.info(f"配置API最大重试次数: {self.max_retries}")

        # 初始化API密钥和基础URL
        logger.info(f"API密钥是否设置: {'是' if config.api_key else '否'}")
        logger.info(f"API基础URL: {config.api_base}")

        # 配置API基础URL
        if config.api_base:
            openai.base_url = config.api_base
            logger.info(f"设置OpenAI API基础URL: {config.api_base}")

        openai.api_key = config.api_key

    def extract_terms(self, text: str, system_prompt: str) -> List[Dict[str, str]]:
        """
        提取文本中的术语及其翻译

        Args:
            text: 要提取术语的文本
            system_prompt: 系统提示

        Returns:
            术语列表，每个术语包含英文和中文
        """
        logger.info("调用术语提取API")

        try:
            # 调用API
            response_text = self._call_api(
                config.chat_model_name, system_prompt, "", temperature=1.3
            )
            return self._extract_terms(response_text)
        except Exception as e:
            logger.warning(f"术语提取失败: {str(e)}")
            return []

    def _extract_terms(self, text: str) -> List[Dict[str, str]]:
        """
        使用正则表达式从响应中提取术语

        Args:
            text: 响应文本
            英文:中文
            英文:中文

        Returns:
            提取的术语列表
        """
        logger.info(f"提取术语:{text}")
        terms = []

        # 匹配 英文:中文 模式
        # 英文术语可以包含空格、数字、字母和连字符
        pattern = r"([^\s:]+.*?)\s*:\s*([^\n]+)"  # 确保英文术语非空
        matches = re.findall(pattern, text)

        if matches:
            logger.info(f"通过正则表达式找到 {len(matches)} 个术语")
            for english, chinese in matches:
                if english.strip():  # 确保英文术语不为空
                    terms.append(
                        {"english": english.strip(), "chinese": chinese.strip()}
                    )
            return terms
        else:
            logger.warning("无法通过正则表达式提取术语")
            return []

    def translate_text(self, text: str, terminology: str) -> str:
        """
        调用API翻译文本

        Args:
            text: 待翻译的文本
            terminology: 术语表字符串
            system_prompt: 系统提示词

        Returns:
            翻译后的文本
        """
        logger.info("调用翻译API")

        # 系统提示词
        system_prompt = f"""
            <角色>你是一位专业的计算机书籍翻译专家
            <任务>将以下英文内容准确翻译为中文
            <要求>
            保持原文技术准确性的同时使用自然流畅的中文表达
            严格使用术语对照表
            技术公式/代码示例保持原文，仅翻译注释部分
            处理长难句时适当拆分但保持逻辑完整
            根据英文内容直接翻译，维持原有的格式，不省略任何信息。
            保留原文的Markdown格式

            <翻译前的原文>
            {text}
            <专有名词>
            {terminology}
            """
        try:
            return self._call_api(
                config.chat_model_name,
                system_prompt=system_prompt,
                user_prompt="",
                temperature=1.3,
            )
        except Exception as e:
            logger.error(f"调用翻译API时出错: {str(e)}")
            # 如果翻译失败，返回原文
            return text

    def polish_translation(
        self, original: str, translation: str, terminology: str
    ) -> str:
        """
        润色翻译

        Args:
            original: 原文
            translation: 初步翻译
            terminology: 术语表

        Returns:
            润色后的翻译
        """
        user_prompt = f"""
你是一名擅长将英文计算机技术书籍翻译为流畅中文表达的翻译员，能够理解英文的俚语、深层次意思，也同样可以用通顺、地道的中文表达。请将一个已有的翻译进行润色

要求：
使用用尽可能地道的简体中文表达
严格遵循术语表译法
信达雅
中文表达专业流畅，无翻译腔
拆分嵌套从句（比如英文长句改为中文流水句）
消除翻译腔（比如减少被字句、“进行”式表达）
技术隐喻本土化\n专业表达校准（如区分验证、校验等技术动词）
原文Markdown格式完整保留

输出：只输出翻译结果文字，不需要输出改动说明、修改建议等

<原文>
{original}

<初步翻译>
{translation}

<专有名词>
{terminology}

        """

        try:
            return self._call_api(
                model_name=config.reasoner_model_name,
                system_prompt="",
                user_prompt=user_prompt,
            )
        except Exception as e:
            logger.error(f"调用翻译润色API时出错: {str(e)}")
            return translation

    def _call_api(
        self,
        model_name: str,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
    ) -> str:
        """
        调用API执行请求

        Args:
            model_name: 模型名称
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            temperature: 温度参数，控制随机性

        Returns:
            API响应文本
        """
        try:
            logger.info("准备调用API")
            logger.info(f"模型: {model_name}")
            logger.info(f"系统提示词: {system_prompt}")
            logger.info(f"用户提示词: {user_prompt}")
            logger.info(f"温度参数: {temperature}")
            logger.info(f"最大Token数: {config.max_tokens}")

            # 创建OpenAI客户端
            client = openai.OpenAI(
                api_key=config.api_key,
                base_url=config.api_base,
                timeout=self.timeout,
                max_retries=3,
            )
            logger.info("已配置API客户端")

            # 调用API
            start_time = time.time()
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=config.max_tokens,
            )
            end_time = time.time()

            # 记录响应信息
            logger.info(f"API调用完成，耗时: {end_time - start_time:.2f}秒")
            logger.info(f"总令牌数: {response.usage.total_tokens}")
            logger.info(f"响应: {response.choices[0].message.content}")

            return response.choices[0].message.content
        except Exception as e:
            error_message = str(e)
            logger.error(f"API调用失败: {error_message}")

            # 添加更详细的错误信息记录
            if hasattr(e, "response"):
                try:
                    response_data = e.response.json()
                    logger.error(f"详细响应: {response_data}")
                    logger.error(f"HTTP状态码: {e.response.status_code}")
                    logger.error(f"响应头: {dict(e.response.headers)}")
                except Exception as parse_error:
                    logger.error(f"无法解析错误响应: {parse_error}")

            raise Exception(f"调用翻译API时出错: {error_message}")


# 创建全局API客户端
api_client = ApiClient()
