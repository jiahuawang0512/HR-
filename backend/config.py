# HR信息日报 - 配置文件

import os
from dotenv import load_dotenv

load_dotenv()

# ========== 数据库配置 ==========
DATABASE_URL = "sqlite:///./hr_daily.db"

# ========== Nature 抓取配置 ==========
# Nature 期刊中的 HR 相关搜索关键词（更精确，避免返回自然科学文章）
NATURE_SEARCH_KEYWORDS = [
    "human resource management workplace",
    "employee engagement productivity",
    "talent management organization",
    "workplace diversity inclusion",
    "organizational behavior psychology",
    "leadership management business",
    "human capital management",
    "workforce analytics",
    "employee wellbeing mental health",
    "remote work productivity",
]

# HBR 中文版 HR 相关过滤关键词（仅保留包含以下关键词的文章）
HBR_CN_HR_KEYWORDS = [
    "人力资源", "人才管理", "招聘", "选拔", "面试", "录用",
    "培训", "发展", "学习", "导师制", "教练",
    "绩效", "KPI", "OKR", "考核", "评估",
    "薪酬", "薪资", "福利", "激励", "奖金",
    "员工", "职场", "敬业度", "满意度", "留存", "离职",
    "HR", "人力", "人事", "员工关系", "劳资",
    "HR科技", "人工智能", "AI", "数字化", "自动化",
    "组织", "领导力", "文化", "团队", "协作",
    "多元化", "包容性", "公平", "偏见", "歧视", "性别平等"
]

# 抓取范围：仅抓取前一天发布的文章（1表示昨天，2表示前天，以此类推）
FETCH_DAYS_AGO = 1

# 请求间隔（秒），避免触发反爬
REQUEST_DELAY = 2

# 失败重试次数
MAX_RETRIES = 3

# ========== 邮件推送配置 ==========
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
USE_TLS = os.getenv("USE_TLS", "True").lower() == "true"
USE_SSL = os.getenv("USE_SSL", "False").lower() == "true"

# 管理员通知邮箱
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "")

# 邮件发件人名称
EMAIL_SENDER_NAME = "HR信息日报"

# ========== 定时任务配置 (CRON 格式) ==========
# 每天抓取时间 (10:30)
FETCH_CRON_HOUR = 10
FETCH_CRON_MINUTE = 30

# 每天推送时间 (10:40)
PUSH_CRON_HOUR = 10
PUSH_CRON_MINUTE = 40

# ========== 系统配置 ==========
# API 文档标题
API_TITLE = "HR信息日报 API"

# API 版本
API_VERSION = "1.0.0"

# 调试模式
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
