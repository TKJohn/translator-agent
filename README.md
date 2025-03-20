# 计算机专业书籍翻译工具

## 项目简介

这是一个专为计算机专业书籍设计的英文到中文翻译工具，可以翻译带有原格式的Markdown文档。该工具使用DeepSeek v3模型进行多步翻译处理，以确保专业术语翻译的准确性和中文语言的流畅性。

## 功能特点

- Markdown的文件翻译，保留原文格式
- 专业术语提取和管理，生成术语表
- 多步翻译流程：
  1. 使用术语表对原文进行翻译
  2. 检查中文语法、表达和通顺度，提供修改建议
  3. 根据修改建议对翻译进行润色
- 批量处理多个文件
- 支持增量更新术语表

## 安装

### 环境要求

- Python 3.8+
- pip 包管理器

### 安装步骤

1. 克隆代码仓库：

```bash
git clone https://github.com/yourusername/translator-agent.git
cd translator-agent
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 创建环境变量文件：

```bash
cp .env.example .env
```

4. 编辑 `.env` 文件，添加你的DeepSeek API密钥

## 使用方法

### 命令行使用

翻译单个HTML文件：

```bash
python src/main.py -i data/input/sample.html -o data/output/sample.md
```

翻译整个目录下的所有文件：

```bash
python src/main.py -i data/input -o data/output
```

使用自定义术语表：

```bash
python src/main.py -i data/input -o data/output -t path/to/your/terminology.csv
```

### 参数说明

- `-i, --input`: 输入Markdown文件或目录路径（必需）
- `-o, --output`: 输出Markdown文件或目录路径（可选）
- `-t, --terminology`: 术语表CSV文件路径（必需）

## 术语表格式

术语表是一个CSV文件，包含以下列：

- `english`: 英文术语
- `chinese`: 中文翻译

例如：

```csv
english,chinese
data structure,数据结构
algorithm,算法
binary search tree,二叉搜索树
```

工具可以提取术语并更新术语表。如果同一术语已有多个翻译，将使用已有的翻译。

## 项目结构

```
translator-agent/
├── src/                      # 源代码
│   ├── main.py               # 主入口程序
│   └── translator/           # 翻译器模块
│       ├── __init__.py       # 包初始化
│       ├── api_client.py     # API客户端
│       ├── config.py         # 配置管理
│       ├── models.py         # 数据模型
│       ├── processor.py      # 处理器
│       ├── terminology_manager.py # 术语管理
│       ├── translator.py     # 翻译器
│       └── utils.py          # 工具函数
├── tests/                    # 测试目录
│   ├── __init__.py           # 测试包初始化
│   ├── conftest.py           # 测试配置
│   ├── run_tests.py          # 测试运行器
│   ├── test_data/            # 测试数据
│   └── test_*.py             # 单元测试文件
├── .env.example              # 环境变量示例
├── requirements.txt          # 依赖列表
└── README.md                 # 项目说明
```

## 注意事项

- 本工具依赖DeepSeek API进行翻译，需要有效的API密钥才能使用
- 处理大型文档可能需要较长时间，请耐心等待
- 专业术语的翻译质量取决于模型的知识和术语表的完整性
- 代码块不会被翻译，将保持原样
- **最大令牌数**：默认设置为8192，可在`.env`文件中通过`MAX_TOKENS`变量修改

## 授权

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 开发与测试

### 运行测试

项目包含完整的单元测试套件，使用pytest框架实现。运行测试前，请先安装测试依赖：

```bash
pip install -r requirements.txt
```

然后运行测试：

```bash
# 运行所有测试
python tests/run_tests.py

# 运行特定模块的测试
python -m pytest tests/test_config.py

# 运行特定测试类
python -m pytest tests/test_models.py::TestTranslationUnit

# 运行特定测试用例
python -m pytest tests/test_models.py::TestTranslationUnit::test_translation_unit_initialization
```

### 测试覆盖率

要生成测试覆盖率报告，请运行：

```bash
python -m pytest --cov=src tests/
```

### 代码风格
#### 代码格式化

本项目使用Black进行代码格式化，以确保代码风格的一致性。Black是一个不妥协的Python代码格式化工具，它会自动格式化代码，使其符合PEP 8规范的子集。

```bash
black src tests
```

#### 代码风格检查
可以使用以下命令检查代码风格：

```bash
flake8 src tests
```
