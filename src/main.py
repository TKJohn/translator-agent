#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
翻译工具主入口 - 命令行界面
"""

import os
import sys
import signal
import argparse

from translator import logger
from translator.processor import Processor
from translator.terminology_manager import TerminologyManager
from translator.translator import Translator


def signal_handler(sig, frame):
    """
    处理中断信号(Ctrl+C)

    Args:
        sig: 信号编号
        frame: 当前栈帧
    """
    print("\n程序已终止")
    sys.exit(0)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="翻译工具 - 将英文Markdown文档翻译为中文"
    )

    # 输入参数
    parser.add_argument(
        "-i", "--input", dest="input_path", help="输入文件或目录路径", required=True
    )

    # 输出参数 - 在extract模式下为可选
    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        help="输出目录路径 (在翻译模式下为必选)",
        required=False,
    )

    # 运行模式
    parser.add_argument(
        "-m",
        "--mode",
        dest="mode",
        choices=["extract", "translate"],
        help="运行模式：'extract' 为术语抽取模式，'translate' 为翻译模式",
        required=True,
    )

    # 术语表文件
    parser.add_argument(
        "-t",
        "--terminology",
        dest="terminology_file",
        help="术语表文件路径 (可选，默认使用配置中的路径)",
        required=False,
    )

    args = parser.parse_args()

    # 在翻译模式下，输出路径为必选
    if args.mode == "translate" and not args.output_path:
        parser.error("翻译模式下，输出路径(-o/--output)为必选参数")

    return args


def main():
    """主函数"""
    # 注册信号处理函数
    signal.signal(signal.SIGINT, signal_handler)

    # 解析命令行参数
    args = parse_args()

    # 处理输入参数
    input_path = os.path.abspath(args.input_path)
    output_path = os.path.abspath(args.output_path) if args.output_path else None

    # 初始化处理器
    terminology_manager = TerminologyManager(args.terminology_file)

    translator = Translator(terminology_manager)

    processor = Processor(
        input_dir=(
            os.path.dirname(input_path) if os.path.isfile(input_path) else input_path
        ),
        output_dir=output_path,
        terminology_manager=terminology_manager,
        translator=translator,
    )

    # 处理翻译或术语抽取
    try:
        if args.mode == "extract":
            logger.info("运行术语抽取模式")
            processor.extract_terminology(input_path)
        else:
            logger.info("运行翻译模式")
            if os.path.isfile(input_path):
                logger.info(f"处理文件: {input_path}")
                processor.translate_file(input_path)
            else:
                logger.info(f"处理目录: {input_path}")
                processor.translate_directory()

        logger.info("操作完成!")
    except KeyboardInterrupt:
        # 捕获Ctrl+C，但不做任何处理，让signal_handler处理
        pass
    except Exception as e:
        logger.error(f"处理过程中发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
