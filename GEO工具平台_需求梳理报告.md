# GEO 工具平台 — 需求梳理报告

> 来源文档：《GEO 工具平台 — 完整开发方案与实施教程》v1.0（2026-06）
> 报告类型：需求梳理 / 范围界定
> 整理日期：2026-06-28

---

## 一、项目背景与定位

### 1.1 一句话定位
面向大模型 RAG 检索体系的内容优化工具。GEO（Generative Engine Optimization，生成式引擎优化）是 SEO 在 AI 时代的演进形态：不再优化页面让搜索引擎爬虫收录，而是优化页面让大语言模型（LLM）的 RAG 检索管道优先**召回、引用、准确理解**你的内容。

### 1.2 GEO 与 SEO 的核心差异

| 维度 | SEO | GEO |
|------|-----|-----|
| 目标受众 | 搜索引擎爬虫（Googlebot 等） | LLM RAG 检索管道（GPT/Claude/Gemini 等） |
| 优化重点 | 关键词密度、链接权重、页面速度 | 实体结构化、JSON-LD 知识图谱、文本分片质量 |
| 评估指标 | 排名、点击率 | AI 采信率、内容被引用次数 |
| 内容形态 | 可读性强的长文 | FAQ / 参数表 / 实体关系 / 标准化分片 |

### 1.3 产品边界
本工具聚焦三大核心场景，外加四项附加能力。范围之外的传统 SEO 功能（关键词排名、外链建设等）**不属于本产品**。

---

## 二、功能需求清单

### 2.1 核心能力（三大场景，必做）

| 编号 | 能力 | 需求描述 | 验收要点 |
|------|------|----------|----------|
| F1 | 内容结构化生成 | 输出符合 LLM RAG 抓取标准的 HTML 页面，内置 JSON-LD 知识图谱、语义标签、分片规范 | 生成的页面为纯静态 HTML，含合法 JSON-LD，可被无 JS 爬虫直读 |
| F2 | GEO 合规检测打分 | 自动扫描页面，从结构化、实体清晰度、语义完整性、时效性四维度评分（满分 100） | 输入 URL/HTML 返回四维分数 + 问题列表 + 优化建议 |
| F3 | 向量优化配套 | 页面文本标准化分片、批量生成 Embedding 向量、导出 RAG 素材包（CSV/JSON） | 输出带元数据的分片包，可直接导入向量库 |

### 2.2 附加能力（增强，按优先级排期）

| 编号 | 能力 | 说明 |
|------|------|------|
| F4 | 批量生成 GEO 文章 | LLM API 调用 + 实体模板填充 |
| F5 | 实体库管理 | 品牌/产品/参数实体的存储与复用 |
| F6 | 站点爬虫自检 | 遵循 robots.txt、限速，批量执行 GEO 打分 |
| F7 | 私有化向量部署 | 本地开源模型（bge-small）+ FAISS/Milvus 离线检索 |

### 2.3 功能模块拆解（对应后端 core 模块）

| 模块 | 文件 | 职责 |
|------|------|------|
| JSON-LD 生成引擎 | `core/jsonld.py` | 支持 Product / FAQPage / Organization / HowTo / Article 五类实体模板，渲染 `<script type="application/ld+json">` 标签 |
| GEO 打分算法 | `core/scorer.py` | 四维度评分（详见下表） |
| 文本分片器 | `core/splitter.py` | 主动输出 200–500 字语义完整分片，每片绑定实体元数据 |
| Embedding 封装 | `core/embedder.py` | 批量向量化，带 Redis 缓存（7 天 TTL）避免重复调用 |
| 实体识别 | `core/ner.py` | NER 抽取品牌/产品/参数/数值 |
| HTML 页面生成 | `core/page_generator.py` | Jinja2 模板输出纯 HTML + 内嵌 JSON-LD + 语义标签 |
| 站点爬虫 | `core/crawler.py` | 异步爬虫，限速、并发控制、同域内链提取 |

---

## 三、GEO 打分模型（核心算法需求）

打分器对目标页面 URL 或 HTML 执行四维度分析，总分 100 分：

| 维度 | 满分 | 检测逻辑 |
|------|------|----------|
| 结构化得分 | 30 | DOM 解析检测 JSON-LD（最重，含多类型加分）、语义标签（`<article>/<dl>/<section>` 等）、FAQ 列表、参数表格 |
| 实体清晰度 | 30 | NER 提取品牌/产品/参数/数值；统计实体密度、唯一标识度、数值参数存在性 |
| 语义完整性 | 25 | Embedding 向量化，页面语义与核心关键词余弦相似度（简化版为标题-正文关键词覆盖率） |
| 时效性/干净度 | 15 | 检测广告弹窗、无关外链、重复段落、过期时间戳 |

> 评分输出结构：`total / structure / entity / semantic / freshness + issues[] + suggestions[]`

---

## 四、技术架构需求

### 4.1 分层架构（前后端分离，4 层）

| 层级 | 组件 | 职责 |
|------|------|------|
| 前端展示层 | Vue 3 + Vite（管理后台） / Next.js（GEO 展示官网） | 可视化操作台：输入产品信息、查看检测报告、批量导出、站点管理 |
| 后端服务层 | Python FastAPI | NLP 核心：实体抽取、语义打分、JSON-LD 生成、文本分片、爬虫调度 |
| 存储层 | PostgreSQL + Redis（进阶 FAISS/Milvus） | 用户数据/实体库/检测记录；向量缓存与任务队列；本地向量检索 |
| AI 依赖层 | Embedding API 或本地开源模型 | OpenAI / 通义千问 Embedding（快速）或 bge-small（私有化离线） |

### 4.2 技术选型（快速上线推荐组合）

| 模块 | 推荐技术 | 理由 |
|------|----------|------|
| 管理后台前端 | Vue 3 + Vite + Element Plus | 开发效率高，组件库完善 |
| GEO 展示官网 | Next.js 14（App Router） | SSG/SSR 静态输出，对 LLM 爬虫友好 |
| 后端 API | Python 3.11 + FastAPI | NLP 生态最佳，async 高并发，自带 OpenAPI 文档 |
| 数据库 | PostgreSQL 16 | JSON 字段存储；pgvector 扩展可直接存向量 |
| 缓存/队列 | Redis 7 | 缓存 Embedding；Celery 任务队列 |
| Embedding | 通义千问 / OpenAI API | 前期不本地部署，按量付费，降低显卡依赖 |
| NER 实体识别 | spaCy + jieba（中文） | 轻量、无需 GPU，规则+统计结合 |
| 爬虫 | aiohttp + BeautifulSoup4 | 异步爬虫，DOM 解析 |

### 4.3 关键接口（API 路由）

| 路由前缀 | 模块 | 用途 |
|----------|------|------|
| `/api/geo` | GEO 生成 | 页面/文章结构化生成 |
| `/api/detect` | 检测打分 | URL/HTML 四维评分 |
| `/api/vector` | 向量处理 | 分片 + Embedding + 导出 |
| `/api/crawler` | 爬虫自检 | 站点批量检测 |
| `/health` | 健康检查 | 服务存活探针 |

---

## 五、非功能需求

| 类别 | 需求 |
|------|------|
| 性能/成本 | Embedding 必须 Redis 缓存（同文本复用，7 天 TTL）；批量调用减少 API 费用 |
| 爬虫合规 | 遵守 robots.txt，1–2 秒请求间隔 + 随机 UA，并发限速防封 IP |
| 静态输出 | GEO 展示页必须纯静态 HTML（Next.js `output:'export'` 或模板渲染），禁止纯 CSR |
| 数据一致性 | JSON-LD 内容必须与页面可见内容一致，否则被大模型降权 |
| 安全 | 生产改默认密码/API Key；PostgreSQL SSL；HTTPS（Let's Encrypt）；Redis 设密码禁外网；FastAPI 关 debug、不暴露 `/docs`；Sentry 错误监控 |
| 部署 | Docker Compose 一键启动；Nginx 反代；生产用 gunicorn + uvicorn workers |

---

## 六、交付形态

| 形态 | 适用场景 | 部署方式 | 优缺点 |
|------|----------|----------|--------|
| SaaS 在线工具 | 多用户付费平台 | Docker 上云（阿里云/腾讯云）+ Nginx + RDS | ✅ 无需客户安装 ❌ 数据在外部 |
| 私有化本地工具 | 企业内网/数据敏感 | Docker Compose 本地 + 本地 bge 向量模型 | ✅ 数据不出网 ❌ 需客户自备服务器 |

---

## 七、实施路线图

### 7.1 7 天 MVP 计划

| 天次 | 任务 | 交付物 |
|------|------|--------|
| Day 1 | FastAPI + PostgreSQL + Redis 基础框架，健康检查、用户鉴权 | 可运行后端骨架 |
| Day 2 | JSON-LD 生成引擎（Product + FAQ 模板） | `POST /api/geo/generate` |
| Day 3 | GEO HTML 页面生成，支持下载 | 静态页生成功能 |
| Day 4 | GEO 打分器（结构化 + 实体两维度），JSON 报告 | `POST /api/detect/url` |
| Day 5 | 文本分片 + Embedding + JSON 导出 | RAG 素材包导出 |
| Day 6 | Vue 3 前端：生成表单 + 检测报告页 | 可用 Web 界面 |
| Day 7 | Docker Compose 打包，本地联调，修复 | 可演示 MVP |

### 7.2 MVP 后进阶路线

| 优先级 | 功能 | 技术实现 |
|--------|------|----------|
| P1 | 站点爬虫批量检测 | aiohttp + Celery + Redis 队列 |
| P1 | 批量生成 GEO 文章 | LLM API + 实体模板填充 |
| P2 | 本地私有化向量部署 | bge-small-zh + FAISS 本地索引 |
| P2 | 语义完整性打分（余弦相似度） | Embedding + numpy 余弦距离 |
| P3 | 实体关系图谱可视化 | D3.js / ECharts |
| P3 | API 对外开放 | FastAPI + Rate Limiting |

---

## 八、关键风险与避坑清单

| # | 风险点 | 应对 |
|---|--------|------|
| 1 | 做成普通 SEO 页面 | GEO 核心是 JSON-LD + 文本分片 + 实体抽取，缺一不可 |
| 2 | Embedding 重复调用产生高额费用 | 同文本向量缓存到 Redis |
| 3 | 展示页用纯 CSR 渲染 | 必须纯静态 HTML，LLM 爬虫不执行 JS |
| 4 | 实体识别只用关键词正则 | 结合 spaCy / jieba + 词性标注，避免同义词/同名异物错判 |
| 5 | 爬虫不限速被封 IP | 遵守 robots.txt，1–2 秒间隔 + 随机 UA |
| 6 | JSON-LD 与页面内容不一致 | 大模型交叉验证，不一致会被降权甚至忽略 |

---

## 九、需求待澄清项（建议与需求方确认）

> 以下为原文档未明确、但落地前需拍板的点：

1. **CSV 导出**：能力描述提到导出 CSV/JSON，但代码示例仅实现 JSON。CSV 是否 MVP 必做？
2. **用户鉴权范围**：Day 1 提到用户鉴权，但未定义角色/多租户/计费模型（SaaS 形态需要）。
3. **Embedding 供应商**：OpenAI 与通义千问二选一的默认值与切换策略未定。
4. **打分维度上线节奏**：语义完整性（余弦相似度）在 MVP 为简化版，正式版依赖 Embedding，需确认 MVP 是否接受简化打分。
5. **实体库**（F5）数据模型、五类实体模板的字段完整性未在文档中给出 schema。
6. **HowTo / Organization 模板**：列为支持但代码示例仅给出 Product/FAQ/Article，需补齐。

---

## 附录：参考资料

| 资源 | 链接 |
|------|------|
| Schema.org 全量实体类型 | https://schema.org/docs/full.html |
| Google 结构化数据测试 | https://search.google.com/test/rich-results |
| spaCy 中文模型文档 | https://spacy.io/models/zh |
| LangChain 文本分片器 | https://python.langchain.com/docs/modules/data_connection/document_transformers/ |
| FastAPI 官方文档 | https://fastapi.tiangolo.com |
| pgvector 向量扩展 | https://github.com/pgvector/pgvector |
