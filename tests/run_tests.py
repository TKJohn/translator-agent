#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试运行脚本
"""

import os
import sys
import pytest


def main():
    """运行所有测试"""
    print("=" * 80)
    print("运行翻译工具测试套件")
    print("=" * 80)

    # 确保测试目录存在
    if not os.path.exists("tests"):
        print("错误: 测试目录不存在")
        sys.exit(1)

    # 运行pytest
    sys.exit(pytest.main())


if __name__ == "__main__":
    main()
