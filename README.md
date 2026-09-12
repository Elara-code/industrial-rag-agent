# 日本企业可信知识问答 Agent

基于 `Elara-code/industrial-rag-agent` 的 Phase 0 可运行原型和后端骨架。

## 已实现

- Agent 工作台：企业维修问题、回答状态、风险提示和多轮输入。
- 引用详情：点击来源后展示文档、页码、部门权限和原文片段。
- 主动拒答：知识库无依据时明确拒答，不编造维修步骤。
- 项目概览：P0/P1/P2 进度、质量指标和使用信号。
- 知识库：文档版本、部门和解析/索引状态。
- 评测中心：准确率、引用正确率、拒答率、延迟与失败归因。
- 反馈与风险：高风险操作、纠正意见和处理状态。
- 后端 API：FastAPI、PostgreSQL + pgvector、S3、DeepSeek、千问 Embedding、百度 OCR 适配配置。
- 评测数据：`data/evaluation_cases.json`，包含 40 条 AX-700 设备保守手册日文问题，覆盖 E-204、故障代码、点检、安全和部品信息。
- 样本文档：`data/sample_documents/`，包含 DOCX、可提取 PDF 和扫描 PDF。
- 评测 API：批量运行评测并保存答案准确率、文档/页码命中率、片段精确率、拒答准确率和逐题耗时/失败原因。

## 运行

```bash
python3 -m http.server 8765
```

打开 `http://127.0.0.1:8001/` 查看前端和后端统一页面：

```bash
.venv/bin/pip install -r requirements.txt
docker compose up -d postgres
.venv/bin/uvicorn backend.app.main:app --reload --port 8001
```
后端默认连接本地 PostgreSQL 的 `5433` 端口（Docker 容器内部仍为 `5432`）。真实运行还需配置 `DEEPSEEK_API_KEY`、`DASHSCOPE_API_KEY`、`BAIDU_API_KEY`、`BAIDU_SECRET_KEY`、`S3_BUCKET` 和 S3 凭据。原生 PDF/TXT 会按页提取并分块；无文本扫描页再使用百度 OCR。百度 OCR 的通用文字识别接口要求将图片 Base64 后通过 HTTPS POST 提交，并使用 API Key/Secret Key 换取 access_token。

千问 `text-embedding-v3` 默认使用 `1024` 维向量；如修改 `EMBEDDING_DIM`，必须同步迁移 PostgreSQL 的 `vector` 列并重新生成已有文档向量。

DeepSeek 默认请求超时为 90 秒，可通过 `DEEPSEEK_TIMEOUT_SECONDS` 调整；千问 Embedding 支持通过 `QWEN_EMBEDDING_BATCH_SIZE` 调整批量大小。

样本文档处理策略：`sample-resume.docx` 走 DOCX 文本解析，`sample-heavy.pdf` 对空白页转图后走百度 OCR，`sample-scanned.pdf` 全部页面转图后走百度 OCR。

运行评测：

```bash
curl -X POST 'http://127.0.0.1:8001/api/projects/demo/evaluations/runs' \
  -H 'Content-Type: application/json' \
  -d '{"limit":40,"user":{"department_id":"生产部","role":"employee","allowed_departments":["生产部"]}}'
```

上传设备保守手册（将路径替换为本地文件路径）：

```bash
curl -X POST 'http://127.0.0.1:8001/api/projects/demo/documents?department_id=%E7%94%9F%E4%BA%A7%E9%83%A8' \
  -F 'file=@/path/to/設備保守マニュアル.pdf;type=application/pdf'
```

查看文档列表和评测详情：

```bash
curl 'http://127.0.0.1:8001/api/projects/demo/documents'
curl 'http://127.0.0.1:8001/api/evaluations/<RUN_ID>'
```
