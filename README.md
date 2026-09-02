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
- 评测数据：`data/evaluation_cases.json`，共 40 条中日文测试问题。
- 样本文档：`data/sample_documents/`，包含 DOCX、可提取 PDF 和扫描 PDF。

## 运行

```bash
python3 -m http.server 8765
```

打开 `http://127.0.0.1:8765/` 查看前端。启动后端：

```bash
pip install -r requirements.txt
docker compose up -d postgres
uvicorn backend.app.main:app --reload
```

后端默认连接本地 PostgreSQL。真实运行还需配置 `DEEPSEEK_API_KEY`、`DASHSCOPE_API_KEY`、`BAIDU_API_KEY`、`BAIDU_SECRET_KEY`、`S3_BUCKET` 和 S3 凭据。原生 PDF/TXT 会按页提取并分块；无文本扫描页再使用百度 OCR。百度 OCR 的通用文字识别接口要求将图片 Base64 后通过 HTTPS POST 提交，并使用 API Key/Secret Key 换取 access_token。

样本文档处理策略：`sample-resume.docx` 需要补充 DOCX 文本解析，`sample-heavy.pdf` 走原生 PDF 提取后人工复核，`sample-scanned.pdf` 走百度 OCR。

上传第一份样本文档：

```bash
curl -X POST 'http://127.0.0.1:8000/api/projects/demo/documents?department_id=生产部' \
  -F 'file=@/Users/liuyawei/Downloads/20160412haieki.pdf;type=application/pdf'
```
