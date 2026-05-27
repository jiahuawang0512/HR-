# HR信息日报 - 邮件推送模块

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from datetime import datetime
from typing import List, Dict, Tuple

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from models import Article


def build_email_content(articles: List[Article], push_date: str) -> str:
    """构建邮件正文HTML"""

    # 计算星期
    weekday_map = {
        0: "星期一",
        1: "星期二",
        2: "星期三",
        3: "星期四",
        4: "星期五",
        5: "星期六",
        6: "星期日"
    }
    date_obj = datetime.strptime(push_date, "%Y-%m-%d")
    weekday = weekday_map[date_obj.weekday()]

    # 日期格式化
    month = date_obj.month
    day = date_obj.day
    date_display = f"{month}月{day}日"

    # 按分类分组文章
    topics_order = [
        "recruitment", "training", "performance", "compensation",
        "employee-relations", "hr-tech", "organizational-behavior", "diversity"
    ]
    topic_labels = {
        "recruitment": "招聘与选拔",
        "training": "培训与发展",
        "performance": "绩效管理",
        "compensation": "薪酬福利",
        "employee-relations": "员工关系",
        "hr-tech": "HR科技与AI",
        "organizational-behavior": "组织行为学",
        "diversity": "多元化与包容性"
    }

    # 按分类整理
    articles_by_topic = {}
    for article in articles:
        topic = article.topic
        if topic not in articles_by_topic:
            articles_by_topic[topic] = []
        articles_by_topic[topic].append(article)

    # 生成文章HTML
    articles_html = ""
    for topic in topics_order:
        if topic not in articles_by_topic:
            continue

        topic_articles = articles_by_topic[topic]
        topic_label = topic_labels.get(topic, topic)

        articles_html += f'''
        <div style="margin-bottom: 30px;">
            <h3 style="color: #1a73e8; font-size: 16px; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #e8f0fe;">
                【{topic_label}】
            </h3>
        '''

        for article in topic_articles:
            # 截取摘要前150字
            summary = article.summary[:150] + "..." if len(article.summary) > 150 else article.summary

            articles_html += f'''
            <div style="background: #f8fafc; border-radius: 8px; padding: 16px; margin-bottom: 12px; border-left: 4px solid #1a73e8;">
                <h4 style="color: #1f2937; font-size: 15px; margin: 0 0 10px 0; line-height: 1.5;">
                    {article.title}
                </h4>
                <p style="color: #6b7280; font-size: 13px; margin: 0 0 10px 0;">
                    <span style="color: #059669;">📚</span> {article.source} &nbsp;|&nbsp;
                    <span style="color: #7c3aed;">✍️</span> {article.authors}
                </p>
                <p style="color: #4b5563; font-size: 14px; line-height: 1.7; margin: 0 0 12px 0;">
                    {summary}
                </p>
                <a href="{article.link}" style="display: inline-block; background: #1a73e8; color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 13px; font-weight: 500;">
                    查看原文 →
                </a>
            </div>
            '''

        articles_html += "</div>"

    # 组装完整HTML
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; background-color: #f3f4f6; font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;">
        <div style="max-width: 680px; margin: 0 auto; padding: 20px;">

            <!-- 头部 -->
            <div style="background: linear-gradient(135deg, #1a365d 0%, #2d3748 100%); border-radius: 16px 16px 0 0; padding: 32px 24px; text-align: center;">
                <h1 style="color: #ffffff; font-size: 24px; margin: 0 0 8px 0; font-weight: 600;">
                    📊 HR信息日报
                </h1>
                <p style="color: rgba(255,255,255,0.85); font-size: 14px; margin: 0;">
                    人力资源管理领域 · 每日最新信息追踪
                </p>
            </div>

            <!-- 日期栏 -->
            <div style="background: #ffffff; padding: 24px; text-align: center; border-bottom: 1px solid #e5e7eb;">
                <div style="display: inline-block; background: #eff6ff; padding: 10px 24px; border-radius: 50px;">
                    <span style="color: #1a73e8; font-size: 18px; font-weight: 600;">
                        📅 {date_display} · {weekday}
                    </span>
                </div>
                <p style="color: #6b7280; font-size: 13px; margin: 12px 0 0 0;">
                    共推送 {len(articles)} 篇精选文章
                </p>
            </div>

            <!-- 文章内容 -->
            <div style="background: #ffffff; padding: 24px; border-radius: 0 0 16px 16px;">
                {articles_html}
            </div>

            <!-- 底部 -->
            <div style="text-align: center; padding: 24px; color: #9ca3af; font-size: 12px;">
                <p style="margin: 0 0 8px 0;">
                    数据来源：Nature (nature.com) · 哈佛商业评论中文版 (hbrchina.org)
                </p>
                <p style="margin: 0;">
                    本邮件由系统自动发送，请勿直接回复
                </p>
            </div>

        </div>
    </body>
    </html>
    '''

    return html


def build_plain_text(articles: List[Article], push_date: str) -> str:
    """构建纯文本版本（兼容不支持HTML的邮件客户端）"""

    weekday_map = {
        0: "星期一", 1: "星期二", 2: "星期三",
        3: "星期四", 4: "星期五", 5: "星期六", 6: "星期日"
    }
    date_obj = datetime.strptime(push_date, "%Y-%m-%d")
    weekday = weekday_map[date_obj.weekday()]

    lines = [
        "=" * 50,
        "📊 HR信息日报",
        "人力资源管理领域 · 每日最新信息追踪",
        "=" * 50,
        "",
        f"📅 {date_obj.month}月{date_obj.day}日 · {weekday}",
        f"共推送 {len(articles)} 篇精选文章",
        "",
        "-" * 50,
    ]

    topic_labels = {
        "recruitment": "【招聘与选拔】",
        "training": "【培训与发展】",
        "performance": "【绩效管理】",
        "compensation": "【薪酬福利】",
        "employee-relations": "【员工关系】",
        "hr-tech": "【HR科技与AI】",
        "organizational-behavior": "【组织行为学】",
        "diversity": "【多元化与包容性】"
    }

    current_topic = None
    for article in articles:
        topic_label = topic_labels.get(article.topic, f"【{article.topic}】")
        if topic_label != current_topic:
            lines.append("")
            lines.append(topic_label)
            current_topic = topic_label

        lines.append(f"🔗 {article.title}")
        lines.append(f"   来源：{article.source} | 作者：{article.authors}")
        lines.append(f"   {article.summary[:80]}...")
        lines.append(f"   链接：{article.link}")
        lines.append("")

    lines.extend([
        "-" * 50,
        "数据来源：Nature (nature.com) · 哈佛商业评论中文版 (hbrchina.org)",
        "本邮件由系统自动发送，请勿直接回复",
    ])

    return "\n".join(lines)


def send_email(to_email: str, subject: str, html_content: str, plain_content: str = "") -> Tuple[bool, str]:
    """发送邮件"""

    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        return False, "邮件服务未配置（SMTP_USER/SMTP_PASSWORD）"

    try:
        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = Header(subject, "utf-8")
        # QQ 邮箱要求 From 格式符合 RFC 5322 标准
        # 正确格式: "发件人名称" <邮箱地址>
        from_email = config.SMTP_USER
        from_name = config.EMAIL_SENDER_NAME
        msg["From"] = formataddr((from_name, from_email))
        msg["To"] = to_email

        # 添加纯文本和HTML版本
        if plain_content:
            msg.attach(MIMEText(plain_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        # 发送邮件
        if config.USE_SSL:
            # 使用 SSL 连接（通常用于 465 端口）
            server = smtplib.SMTP_SSL(config.SMTP_HOST, config.SMTP_PORT)
        elif config.USE_TLS:
            # 使用 STARTTLS（通常用于 587 端口）
            server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT)

        server.login(config.SMTP_USER, config.SMTP_PASSWORD)
        server.sendmail(config.SMTP_USER, [to_email], msg.as_string())
        server.quit()

        return True, "发送成功"

    except smtplib.SMTPAuthenticationError:
        return False, "邮箱认证失败，请检查用户名和密码"
    except smtplib.SMTPRecipientsRefused:
        return False, "收件人地址被拒绝"
    except smtplib.SMTPException as e:
        return False, f"SMTP错误: {str(e)}"
    except Exception as e:
        return False, f"发送失败: {str(e)}"


def push_to_subscriber(subscriber_email: str, articles: List[Article], push_date: str) -> Tuple[bool, str]:
    """向单个订阅者发送推送邮件"""

    # 构建邮件主题
    date_obj = datetime.strptime(push_date, "%Y-%m-%d")
    subject = f"【HR信息日报】{date_obj.month}月{date_obj.day}日 · 今日推送{len(articles)}篇"

    # 构建邮件内容
    html_content = build_email_content(articles, push_date)
    plain_content = build_plain_text(articles, push_date)

    # 发送
    return send_email(subscriber_email, subject, html_content, plain_content)


def push_daily(articles: List[Article], subscribers: List[Dict], push_date: str) -> Dict:
    """向所有订阅者发送每日推送"""

    results = {
        "total": len(subscribers),
        "success": 0,
        "failed": 0,
        "errors": []
    }

    if not articles:
        results["errors"].append("没有待推送的文章")
        return results

    if not subscribers:
        results["errors"].append("没有活跃订阅者")
        return results

    for subscriber in subscribers:
        email = subscriber.get("email", "")
        if not email:
            continue

        success, message = push_to_subscriber(email, articles, push_date)

        if success:
            results["success"] += 1
        else:
            results["failed"] += 1
            results["errors"].append(f"{email}: {message}")

    return results


if __name__ == "__main__":
    # 测试邮件发送
    print("邮件推送模块测试")
    print("请先在 config.py 中配置 SMTP 信息")
