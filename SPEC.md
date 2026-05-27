# HR信息日报系统 - 技术规格文档

## 1. 项目概述

### 项目名称
HR信息日报自动推送系统

### 核心功能
- 每日自动从 Nature 官网检索 HR 人力资源管理领域最新研究文章
- 每日自动从哈佛商业评论 (HBR) 检索管理学领域最新文章
- 支持来源筛选（Nature / HBR / 全部）
- 每天中午 12:00 定时抓取并推送
- 通过邮件将推送内容发送给订阅用户
- Web 界面展示历史推送内容

### 目标用户
- HR 从业者
- 人力资源管理研究者
- 企业管理决策者

---

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    系统架构图                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │  Nature.com  │───▶│  抓取模块    │───▶│  SQLite   │ │
│  │  官网        │    │  (Scraper)   │    │  数据库    │ │
│  └──────────────┘    └──────────────┘    └─────┬─────┘ │
│                                               │        │
│  ┌──────────────┐    ┌──────────────┐          │        │
│  │  前端界面    │◀───│  FastAPI     │◀─────────┘        │
│  │  (已存在)    │    │  Backend     │                   │
│  └──────────────┘    └──────┬───────┘                   │
│                             │                           │
│                      ┌──────▼───────┐                   │
│                      │  APScheduler │                   │
│                      │  定时任务     │                   │
│                      │  每日12:00   │                   │
│                      └──────┬───────┘                   │
│                             │                           │
│                      ┌──────▼───────┐                   │
│                      │  邮件推送     │                   │
│                      │  (SMTP)      │                   │
│                      └──────────────┘                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 技术栈

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| 后端框架 | FastAPI | 高性能异步 API 框架 |
| 数据库 | SQLite | 轻量级，无需额外部署 |
| 定时任务 | APScheduler | Python 定时调度 |
| 网页抓取 | requests + BeautifulSoup | Nature 文章抓取 |
| 邮件发送 | smtplib | 标准库，无额外依赖 |
| 前端 | 现有 HTML/CSS/JS | 已有界面 |

---

## 4. 数据库设计

### 表结构：articles（文章表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER PRIMARY KEY | 自增主键 |
| nature_id | TEXT UNIQUE | Nature/HBR 文章 ID |
| title | TEXT | 文章标题 |
| title_en | TEXT | 英文标题 |
| summary | TEXT | 中文摘要 |
| source | TEXT | 来源期刊 (Nature / Harvard Business Review) |
| source_short | TEXT | 来源简称 (Nature / HBR) |
| authors | TEXT | 作者列表 |
| link | TEXT | 原文链接 |
| topic | TEXT | 分类标签 |
| topic_label | TEXT | 分类中文名 |
| publish_date | TEXT | 发布日期 |
| fetched_date | TEXT | 抓取日期 |
| push_date | TEXT | 推送日期 |
| is_pushed | INTEGER | 是否已推送 (0/1) |

### 表结构：subscribers（订阅者表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER PRIMARY KEY | 自增主键 |
| email | TEXT UNIQUE | 邮箱地址 |
| interests | TEXT | 感兴趣领域 (JSON) |
| is_active | INTEGER | 订阅状态 (0/1) |
| created_at | TEXT | 创建时间 |
| last_push_at | TEXT | 最后推送时间 |

### 表结构：push_logs（推送日志表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER PRIMARY KEY | 自增主键 |
| push_date | TEXT | 推送日期 |
| article_count | INTEGER | 推送文章数 |
| success_count | INTEGER | 成功发送数 |
| failed_count | INTEGER | 失败数 |
| status | TEXT | 状态 (success/failed/partial) |
| error_message | TEXT | 错误信息 |

---

## 5. API 接口设计

### 基础信息
- Base URL: `http://localhost:8080/api`
- 响应格式: JSON

### 接口列表

#### 5.1 获取文章列表
```
GET /api/articles

Query Parameters:
  - date: 可选，筛选日期 (YYYY-MM-DD)
  - topic: 可选，筛选领域
  - source: 可选，筛选来源 (Nature/HBR/all)
  - page: 可选，页码 (default: 1)
  - page_size: 可选，每页数量 (default: 10)

Response:
{
  "code": 200,
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 10,
    "source": "all",
    "articles": [...]
  }
}
```

#### 5.2 获取单篇文章详情
```
GET /api/articles/{id}

Response:
{
  "code": 200,
  "data": { article object }
}
```

#### 5.3 获取推送日历
```
GET /api/push-calendar

Response:
{
  "code": 200,
  "data": [
    {"date": "2026-04-20", "article_count": 4, "weekday": "星期一"},
    {"date": "2026-04-19", "article_count": 0, "weekday": "星期日"},
    ...
  ]
}
```

#### 5.4 订阅推送
```
POST /api/subscribe

Request Body:
{
  "email": "user@example.com",
  "interests": ["recruitment", "training", "performance"]
}

Response:
{
  "code": 200,
  "message": "订阅成功"
}
```

#### 5.5 取消订阅
```
POST /api/unsubscribe

Request Body:
{
  "email": "user@example.com"
}

Response:
{
  "code": 200,
  "message": "已取消订阅"
}
```

#### 5.6 手动触发抓取（管理员）
```
POST /api/admin/fetch

Response:
{
  "code": 200,
  "message": "抓取成功",
  "data": {"fetched": 5, "new": 3}
}
```

#### 5.7 手动触发推送（管理员）
```
POST /api/admin/push

Response:
{
  "code": 200,
  "message": "推送成功",
  "data": {"sent": 45, "failed": 2}
}
```

#### 5.8 获取系统状态
```
GET /api/admin/status

Response:
{
  "code": 200,
  "data": {
    "total_articles": 120,
    "total_subscribers": 45,
    "last_fetch": "2026-04-20 12:00:00",
    "last_push": "2026-04-20 12:05:32",
    "next_push": "2026-04-21 12:00:00",
    "scheduler_running": true
  }
}
```

#### 5.9 获取可用领域列表
```
GET /api/topics

Response:
{
  "code": 200,
  "data": [
    {"value": "recruitment", "label": "招聘与选拔"},
    {"value": "training", "label": "培训与发展"},
    ...
  ]
}
```

#### 5.10 获取来源列表
```
GET /api/sources

Response:
{
  "code": 200,
  "data": [
    {"value": "all", "label": "全部来源"},
    {"value": "Nature", "label": "Nature"},
    {"value": "HBR", "label": "哈佛商业评论"}
  ]
}
```

---

## 6. 定时任务设计

### 任务1：每日文章抓取
- 时间：每天 11:50 (推送前10分钟)
- 说明：优先抓取当天新文章

### 任务2：每日推送
- 时间：每天 12:00
- 说明：向所有订阅用户发送当日文章摘要邮件

### 任务3：每周数据清理
- 时间：每周一 00:00
- 说明：清理超过1年的推送日志

---

## 7. 邮件模板设计

### 邮件主题
```
【HR信息日报】2026年4月20日 · 今日推送4篇
```

### 邮件正文结构
```
亲爱的订阅者：

您关注的 HR信息日报 已更新，以下是今日精选内容：

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📅 2026年4月20日 · 星期一
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【招聘与选拔】
🔗 AI算法会选择你的下一位实验室同事吗？
来源：Nature | 作者：Linda Nordling
摘要：...
[查看原文](link)

【员工关系】
🔗 远程工作如何塑造工作与家庭平衡？
来源：Humanities and Social Sciences | 作者：Te Li, Wen Yang
摘要：...
[查看原文](link)

... (更多文章)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 今日共推送 4 篇
数据来源：Nature (nature.com)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

退订链接：[unsubscribe_url]
```

---

## 8. Nature 抓取策略

### 搜索关键词池
```
- human resource management
- employee engagement
- recruitment hiring
- performance management
- organizational behavior
- workplace wellbeing
- talent management
- leadership
- AI HR artificial intelligence
- diversity inclusion
```

### 抓取规则
1. 每次抓取最近 7 天内发布的文章
2. 去重依据：nature_id
3. 自动分类依据：关键词匹配
4. 摘要优先使用文章提供的英文摘要翻译

### 异常处理
- 网络超时：重试3次，间隔10秒
- 反爬限制：每次请求间隔2秒
- 数据异常：记录日志，人工介入

---

## 9. 文件结构

```
/Users/wangjiahua/CodeBuddy/20260417155133/
├── SPEC.md                    # 本文档
├── backend/
│   ├── __init__.py
│   ├── main.py               # FastAPI 入口
│   ├── config.py             # 配置文件
│   ├── database.py           # 数据库操作
│   ├── models.py             # 数据模型
│   ├── scraper.py            # Nature 抓取模块
│   ├── scraper_hbr.py        # HBR 抓取模块
│   ├── seed.py               # Nature 数据初始化
│   ├── seed_hbr.py           # HBR 数据初始化
│   ├── scheduler.py          # 定时任务
│   ├── pusher.py             # 邮件推送
│   ├── api.py                # API 路由
│   └── requirements.txt      # 依赖
├── index.html                # 前端页面
├── styles.css
├── app.js
└── README.md
```

---

## 10. 部署说明

### 本地运行
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 配置项（.env 或 config.py）
```python
# 邮件配置
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"

# 管理员邮箱（接收错误通知）
ADMIN_EMAIL = "admin@example.com"

# 推送时间 (CRON 格式)
PUSH_CRON = "0 12 * * *"  # 每天12:00
FETCH_CRON = "50 11 * * *"  # 每天11:50
```

---

## 11. 未来扩展方向

- [ ] 接入微信公众号/小程序推送
- [ ] 接入飞书/钉钉 Webhook 推送
- [ ] 增加文章收藏和笔记功能
- [ ] 增加阅读量统计
- [ ] 接入 Semantic Scholar API 获取更多元数据
- [ ] Docker 容器化部署
