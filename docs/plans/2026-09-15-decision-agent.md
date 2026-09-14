# 制造企业设备保全决策 Agent Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在现有可信知识问答系统上，完成 AX-700 E-204 的趋势分析、规则决策和人工确认闭环。

**Architecture:** 保留当前 FastAPI + PostgreSQL/pgvector + S3 + DeepSeek + 千问 + 百度 OCR。新增少量运营数据表和确定性规则模块；SQL 负责趋势，规则负责安全边界，RAG 负责证据，LLM 负责解释，前端展示决策路径和确认状态。

**Tech Stack:** FastAPI、SQLAlchemy、PostgreSQL、pgvector、原生 HTML/CSS/JavaScript、现有 LLM/OCR/Embedding 适配器。

---

## Task 1: 固定 P0 决策数据契约

**Files:**
- Create: `data/decision_events.json`
- Create: `data/decision_rules.json`
- Modify: `docs/decision-agent-product-design.md`

**步骤：**

1. 生成 10 台 AX-700 设备、6 个月故障事件和维护记录。
2. 至少覆盖 E-204 正常、重复、升级和数据不足四种场景。
3. 为 E-204 写出条件、动作、禁止动作、升级条件和来源页码。
4. 校验每条事件都有设备编号、时间、故障码和来源。

**验收：** 数据可加载；同一设备可以计算 7 天、30 天和 90 天趋势；规则能覆盖至少 4 个 E-204 分支。

## Task 2: 增加运营数据表和种子加载

**Files:**
- Modify: `backend/app/main.py`
- Create: `backend/app/operations.py`
- Test: `backend/tests/test_operations.py`

**步骤：**

1. 增加 `Asset`、`AlarmEvent`、`MaintenanceRecord` 三个最小模型。
2. 增加开发环境种子加载函数，重复执行不得产生重复记录。
3. 增加按项目、部门、设备和时间范围过滤的查询函数。
4. 用内置断言测试时间范围和部门权限过滤。

**验收：** 运营数据不能读取到其他部门；空时间范围返回明确的数据不足状态。

## Task 3: 实现趋势分析 API

**Files:**
- Create: `backend/app/trends.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_trends.py`

**步骤：**

1. 实现故障次数按天/周聚合。
2. 实现设备风险排名和重复故障间隔。
3. 实现运行小时与故障事件的关联查询。
4. 暴露 `GET /api/projects/{project_id}/trends`。
5. 无数据时返回 `insufficient_data=true`，不返回趋势结论。

**验收：** API 返回数据范围、聚合粒度、趋势序列和数据不足原因；所有结果可按部门过滤。

## Task 4: 实现 E-204 确定性决策规则

**Files:**
- Create: `backend/app/decision_engine.py`
- Test: `backend/tests/test_decision_engine.py`

**步骤：**

1. 定义 `DecisionInput`：设备、故障码、运行小时、最近次数、连接器状态和传感器结果。
2. 定义 `DecisionResult`：风险、结论、动作、禁止动作、升级条件、缺失条件和规则来源。
3. 实现 E-204 的最小分支判断。
4. 增加高风险动作拦截：未断电、持续过热或信息不足时不得建议继续运行。
5. 为正常、重复、连接器腐蚀、传感器异常和数据不足写回归测试。

**验收：** 同一输入得到稳定结果；关键事实和禁止动作不由 LLM 改写。

## Task 5: 接入决策 Agent API

**Files:**
- Modify: `backend/app/main.py`
- Modify: `backend/app/decision_engine.py`
- Test: `backend/tests/test_decision_api.py`

**步骤：**

1. 暴露 `POST /api/projects/{project_id}/decisions`。
2. 先做权限过滤、运营数据查询和规则判断。
3. 缺少关键条件时返回追问，不调用 LLM 生成确定结论。
4. 有规则结果时让 DeepSeek 只负责解释和组织语言。
5. 保存输入、规则版本、证据、模型状态和人工确认状态。

**验收：** 返回结论、路径、动作、风险、引用和审计 ID；服务配置缺失时返回可理解错误。

## Task 6: 重做前端健康总览和决策工作台

**Files:**
- Modify: `index.html`
- Modify: `app.js`
- Modify: `style.css`

**步骤：**

1. 将“项目概览”改为真实数据范围、设备数、故障数和风险数看板。
2. 增加趋势卡片，点击后进入 E-204 决策工作台。
3. 增加场景条件表单和缺失条件提示。
4. 展示决策路径、执行清单、禁止动作和证据引用。
5. 高风险结论增加“确认后执行”按钮，未确认前不显示为已执行。

**验收：** 无数据、接口失败、规则拒绝和待人工确认都有明确页面状态；不出现硬编码生产指标。

## Task 7: 扩展决策评测集和评测 API

**Files:**
- Create: `data/decision_evaluation_cases.json`
- Modify: `backend/app/main.py`
- Modify: `backend/tests/test_core.py`

**步骤：**

1. 增加趋势上升、趋势稳定、数据不足、应升级和禁止继续运行案例。
2. 评分拆分为趋势、动作、风险、升级、证据和拒答。
3. 保存逐题输入、实际路径、标准路径和失败归因。
4. 前端展示每项指标和失败题详情。

**验收：** 评测结果可以复现；错误数字、故障码和危险动作不能被语义相似度兜底放过。

## Task 8: P0 集成验证和发布门禁

**Files:**
- Modify: `README.md`
- Create: `docs/decision-agent-acceptance.md`

**步骤：**

1. 启动 PostgreSQL/pgvector 和 FastAPI 8001。
2. 加载种子数据并验证权限过滤。
3. 验证趋势 API、E-204 决策 API 和前端完整路径。
4. 在配置完整环境下运行决策评测集。
5. 记录性能、失败原因和已知限制，使用中文提交说明。

**验收：** P0 场景可从趋势卡片进入决策、查看证据、确认动作并留下审计记录。

## 后续 P1 任务

- 接入 E-101、E-205、E-301 的决策规则。
- 增加真实反馈和人工评分队列。
- 增加维护计划和备件建议。
- 接入 CMMS/MES/ERP 的只读数据同步。
- 增加异步任务、失败重试和通知。

## 暂不实施

- PLC 自动控制。
- 黑盒预测性维护模型。
- 企业级单点登录。
- 全量 ERP/MES 写入。
