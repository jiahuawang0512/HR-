"""
GitHub Actions: 每日邮件推送脚本

需要的环境变量（放在 GitHub Secrets）：
- SMTP_HOST       默认 smtp.qq.com
- SMTP_PORT       默认 465
- SMTP_USER       发件邮箱
- SMTP_PASSWORD   邮箱授权码
- USE_SSL         默认 True
- USE_TLS         默认 False
- MAIL_TO         收件人邮箱，多个用逗号或分号分隔
"""

import os
import sys
from datetime import datetime

# 把 backend 目录加入 sys.path，使得 import config / database / pusher / models 与项目保持一致
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_DIR = os.path.join(ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

import database  # noqa: E402
import pusher  # noqa: E402
from models import Article  # noqa: E402


def get_recipients():
    raw = os.getenv("MAIL_TO", "").strip()
    if not raw:
        return []
    return [e.strip() for e in raw.replace(";", ",").split(",") if e.strip()]


def get_latest_push_date():
    with database.get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT push_date FROM articles WHERE push_date IS NOT NULL ORDER BY push_date DESC LIMIT 1")
        row = cur.fetchone()
        return row[0] if row else ""


def get_articles_by_date(push_date):
    with database.get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT nature_id, title, title_en, summary, source, source_short,
                   authors, link, topic, topic_label, publish_date, fetched_date,
                   push_date, is_pushed
            FROM articles
            WHERE push_date = ?
            ORDER BY topic, id
            """,
            (push_date,),
        )
        rows = cur.fetchall()

    articles = []
    for r in rows:
        a = Article(
            nature_id=r["nature_id"] or "",
            title=r["title"] or "",
            title_en=r["title_en"] or "",
            summary=r["summary"] or "",
            source=r["source"] or "",
            source_short=r["source_short"] or "",
            authors=r["authors"] or "",
            link=r["link"] or "",
            topic=r["topic"] or "",
            topic_label=r["topic_label"] or "",
            publish_date=r["publish_date"] or "",
            fetched_date=r["fetched_date"] or "",
            push_date=r["push_date"] or "",
            is_pushed=bool(r["is_pushed"]),
        )
        articles.append(a)
    return articles


def main():
    recipients = get_recipients()
    if not recipients:
        print("[email] MAIL_TO 未配置，跳过邮件发送")
        return 0

    if not os.getenv("SMTP_USER") or not os.getenv("SMTP_PASSWORD"):
        print("[email] SMTP_USER / SMTP_PASSWORD 未配置，跳过邮件发送")
        return 0

    # 优先取今天的；没有则取最新一期（保证"每天都发"）
    today = datetime.now().strftime("%Y-%m-%d")
    articles = get_articles_by_date(today)
    push_date = today

    if not articles:
        latest = get_latest_push_date()
        if not latest:
            print("[email] 数据库无任何文章，跳过")
            return 0
        push_date = latest
        articles = get_articles_by_date(push_date)
        print(f"[email] 今日({today}) 无新文章，回退到最新一期 {push_date}（{len(articles)} 篇）")
    else:
        print(f"[email] 推送 {push_date}（{len(articles)} 篇）到 {len(recipients)} 个收件人")

    success_cnt, fail_cnt, errors = 0, 0, []
    for to_email in recipients:
        ok, msg = pusher.push_to_subscriber(to_email, articles, push_date)
        if ok:
            success_cnt += 1
            print(f"[email] OK   -> {to_email}")
        else:
            fail_cnt += 1
            errors.append(f"{to_email}: {msg}")
            print(f"[email] FAIL -> {to_email}: {msg}")

    print(f"[email] 完成：成功 {success_cnt} / 失败 {fail_cnt}")
    if errors:
        for e in errors:
            print("  -", e)

    # 全部失败才返回非零
    return 1 if success_cnt == 0 and fail_cnt > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
