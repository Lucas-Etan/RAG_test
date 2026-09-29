# RAG_test

一个用于验证 RAG（检索增强生成）流程的测试项目。

项目的重点在**检索环节**：把资料切分成小块、向量化、按余弦相似度召回，最后把命中的资料拼成上下文。
它本身不调用大模型生成回答，`answer_with_context` 只是把检索到的资料套进模板输出，方便你直观地检查"这个问题到底召回了哪些资料块"。

## 目录结构

```
RAG_test/
├── main.py               # 入口：遍历 QUESTIONS 列表，逐条提问并打印结果
├── bulid_chunk.py        # 构建索引的脚本（注意文件名拼写为 bulid）
├── chunker.py            # 读取资料文件 + 按行切分
├── embedding_vector.py   # 调用 Ollama 做向量化，提供归一化和余弦相似度
├── retriever.py          # 检索：算相似度、排序、按阈值过滤
├── rag_answer.py         # 把检索结果拼成上下文，返回答案
├── docs/
│   └── test.json         # 资料源文件（每行一个知识点）
├── index/
│   └── chunks.json       # 切分后的索引（只存文本，不存向量）
├── requirements.txt
└── .env                  # 环境变量（已被 .gitignore 忽略）
```

## 工作流程

```
docs/test.json
      │  ① bulid_chunk.py（离线，一次性）
      ▼
chunker.split_by_line()  →  index/chunks.json
                                  │
                                  │  ② main.py 运行时
                                  ▼
提问 ──→ embed_text() ──→ retriever.retrieve()
                              │  余弦相似度排序，取 top_k 且 > SCORE_THRESHOLD
                              ▼
                    rag_answer.build_context()
                              │  格式化成 [id|source] 正文
                              ▼
                          打印答案和来源
```

## 环境准备

### 1. 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

依赖只有两个：`numpy`（向量计算）和 `dotenv`（读取 `.env`）。

### 2. 启动 Ollama 并准备向量模型

```bash
ollama serve
ollama pull <你的向量模型名>
```

### 3. 配置 .env

在项目根目录创建 `.env`，两个变量都是**必填**，缺失时 `embedding_vector.py` 会在导入阶段直接抛 `RuntimeError`：

```ini
OLLAMA_BASE_URL=http://localhost:11434
EMBED_MODEL=<你的向量模型名>
```

## 使用方法

### 第一步：构建索引

资料源文件是 `docs/test.json`，格式上按**每行一个知识点**来写（不需要是合法 JSON）。改完资料后运行：

```bash
python bulid_chunk.py
```

它会重新切分并覆盖写入 `index/chunks.json`。

### 第二步：提问

在 `main.py` 顶部的 `QUESTIONS` 列表里写入问题，然后运行：

```bash
python main.py
```

输出格式：

```
================================================================================
Q: What is this project for?
根据资料：
[chunk_000|docs/test.json] This is a project for testing RAG

针对问题"What is this project for?"，可依据上述资料作答。
sources: ['chunk_000', 'chunk_...', 'chunk_...'] grounded: False
```

`sources` 就是这次命中的资料块 id，用它来判断召回质量。

## 核心参数

| 参数 | 位置 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `SCORE_THRESHOLD` | `retriever.py` | `0.35` | 相似度阈值，**严格大于**才会被保留 |
| `top_k` | `retrieve()` | `3` | 最多返回几条资料 |
| `source_path` | `bulid_chunk.py` | `docs/test.json` | 资料源文件路径 |

## 实现细节与已知限制

这些都是当前代码的实际行为，使用前需要了解：

- **不生成回答。** `answer_with_context` 没有接入大模型，返回的"答案"只是检索结果的拼接模板。如果要接 LLM，改 `rag_answer.py` 即可。
- **`grounded` 恒为 `False`。** `rag_answer.py` 里是硬编码的，目前不代表任何实际判断。
- **向量不落盘。** `index/chunks.json` 只存 `id` / `text` / `source`，向量在每次运行时现算。`retriever.py` 里的 `_CHUNK_CACHE` 只是进程内缓存，所以**每次运行 `main.py` 都会重新请求一遍所有资料块的 embedding**（当前 17 块 = 启动时 17 次 HTTP 请求）。资料变多后这里会成为瓶颈。
- **切分策略很粗糙。** `split_by_line` 只按行切，每行一个块，没有重叠窗口；一行太长会超出模型的上下文，一行太短又缺少上下文信息。
- **id 可能不连续。** id 由 `enumerate(text.splitlines())` 的行号生成，空行虽然会被跳过，但行号照常累加，所以资料中夹空行会导致 id 出现跳号。
- **首次检索较慢。** 第一次调用会把所有资料块依次送去向量化，是串行的，也没有批量接口。
