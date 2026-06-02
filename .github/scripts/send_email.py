"""
GitHub Actions: 每日邮件推送脚本

订阅者来源（优先级从高到低）：
1) 环境变量 MAIL_TO （逗号分隔，便于临时调试）
2) 仓库根目录 subscribers.json （由 EdgeOne Pages Function 写入，前端订阅按钮的来源）
3) 数据库 subscribers 表中 is_active=1 的全部用户（历史兼容）

需要的环境变量（GitHub Secrets）：
- SMTP_USER       发件邮箱
- SMTP_PASSWORD   邮箱授权码
- SMTP_HOST       默认 smtp.qq.com
- SMTP_PORT       默认 465
- USE_SSL         默认 True
- USE_TLS         默认 False
- MAIL_TO         可选，覆盖订阅表
"""

import os
import sys
import json
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND_DIR = os.path.join(ROOT, "backend")
sys.path.insert(0, BACKEND_DIR)

import database  # noqa: E402
import pusher  # noqa: E402
from models import Article  # noqa: E402


SUBSCRIBERS_JSON = os.path.join(ROOT, "subscribers.json")


def get_recipients_from_env():
    raw = os.getenv("MAIL_TO", "").strip()
    if not raw:
        return []
    return [e.strip() for e in raw.replace(";", ",").split(",") if e.strip()]


def get_recipients_from_json():
    """读取仓库根目录 subscribers.json，过滤掉 active=False"""
    if not os.path.exists(SUBSCRIBERS_JSON):
        return []
    try:
        with open(SUBSCRIBERS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        emails = []
        for s in data.get("subscribers", []) or []:
            email = (s.get("email") or "").strip()
            if email and s.get("active", True):
                emails.append(email)
        # 去重，保持顺序
        seen, uniq = set(), []
        for e in emails:
            k = e.lower()
            if k not in seen:
                seen.add(k)
                uniq.append(e)
        return uniq
    except Exception as exc:
        print(f"[email] 读取 subscribers.json 失败: {exc}")
        return []


def get_recipients_from_db():
    """读取订阅者表中所有 is_active=1 的邮箱（历史兼容）"""
    try:
        with database.get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT email FROM subscribers WHERE is_active=1 ORDER BY id")
            rows = cur.fetchall()
        return [r[0] for r in rows if r[0]]
    except Exception as exc:
        print(f"[email] 读取数据库订阅者失败: {exc}")
        return []


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


def update_last_push_at(emails, push_date):
    """更新订阅者 last_push_at 字段"""
    if not emails:
        return
    now = datetime.now().isoformat()
    with database.get_db() as conn:
        cur = conn.cursor()
        cur.executemany(
            "UPDATE subscribers SET last_push_at=? WHERE email=?",
            [(now, e) for e in emails],
        )


def main():
    # 1. 检查 SMTP 配置
    if not os.getenv("SMTP_USER") or not os.getenv("SMTP_PASSWORD"):
        print("[email] SMTP_USER / SMTP_PASSWORD 未配置，跳过邮件发送")
        return 0

    # 2. 选择收件人来源
    recipients = get_recipients_from_env()
    if recipients:
        print(f"[email] 使用 MAIL_TO 环境变量中的 {len(recipients)} 个收件人")
    else:
        from_json = get_recipients_from_json()
        from_db = get_recipients_from_db()
        # 合并去重，保持 json 优先顺序
        seen, recipients = set(), []
        for e in from_json + from_db:
            k = (e or "").lower()
            if k and k not in seen:
                seen.add(k)
                recipients.append(e)
        if not recipients:
            print("[email] subscribers.json 与数据库均无活跃订阅者，跳过邮件发送")
            return 0
        print(f"[email] 订阅者来源 -> json:{len(from_json)} db:{len(from_db)} 合并后 {len(recipients)}: {recipients}")

    # 3. 获取要推送的文章（优先今天，否则最新一期）
    today = datetime.now().strftime("%Y-%m-%d")
    push_date = today
    articles = get_articles_by_date(push_date)
    if not articles:
        latest = get_latest_push_date()
        if not latest:
            print("[email] 数据库无任何文章，跳过")
            return 0
        push_date = latest
        articles = get_articles_by_date(push_date)
        print(f"[email] 今日({today}) 无新文章，回退到最新一期 {push_date}（{len(articles)} 篇）")
    else:
        print(f"[email] 推送 {push_date}（{len(articles)} 篇）")

    # 4. 逐个发送
    success_cnt, fail_cnt, errors, success_emails = 0, 0, [], []
    for to_email in recipients:
        ok, msg = pusher.push_to_subscriber(to_email, articles, push_date)
        if ok:
            success_cnt += 1
            success_emails.append(to_email)
            print(f"[email] OK   -> {to_email}")
        else:
            fail_cnt += 1
            errors.append(f"{to_email}: {msg}")
            print(f"[email] FAIL -> {to_email}: {msg}")

    # 5. 更新 last_push_at
    if success_emails:
        try:
            update_last_push_at(success_emails, push_date)
        except Exception as e:
            print(f"[email] 更新 last_push_at 失败: {e}")

    print(f"[email] 完成：成功 {success_cnt} / 失败 {fail_cnt}")
    if errors:
        for e in errors:
            print("  -", e)

    return 1 if success_cnt == 0 and fail_cnt > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
