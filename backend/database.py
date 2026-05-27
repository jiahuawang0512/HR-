# HR信息日报 - 数据库操作模块

import sqlite3
from datetime import datetime
from typing import Optional, List
from contextlib import contextmanager

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Article, Subscriber, PushLog


# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hr_daily.db")


def get_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db():
    """数据库上下文管理器"""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def init_database():
    """初始化数据库表"""
    with get_db() as conn:
        cursor = conn.cursor()

        # 文章表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nature_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                title_en TEXT,
                summary TEXT NOT NULL,
                source TEXT NOT NULL,
                source_short TEXT,
                authors TEXT NOT NULL,
                link TEXT NOT NULL,
                topic TEXT NOT NULL,
                topic_label TEXT NOT NULL,
                publish_date TEXT NOT NULL,
                fetched_date TEXT NOT NULL,
                push_date TEXT,
                is_pushed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 检查并添加 source_short 列（如果不存在）
        cursor.execute("PRAGMA table_info(articles)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'source_short' not in columns:
            cursor.execute("ALTER TABLE articles ADD COLUMN source_short TEXT")

        # 订阅者表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscribers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                interests TEXT DEFAULT '[]',
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                last_push_at TEXT
            )
        """)

        # 推送日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS push_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                push_date TEXT NOT NULL,
                article_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                failed_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'pending',
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_nature_id ON articles(nature_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_push_date ON articles(push_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_is_pushed ON articles(is_pushed)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subscribers_email ON subscribers(email)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_push_logs_push_date ON push_logs(push_date)")


# ========== 文章操作 ==========
def insert_article(article: Article) -> Optional[int]:
    """插入文章，返回ID，失败返回None（已存在或异常）"""
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO articles (
                    nature_id, title, title_en, summary, source, source_short, authors, link,
                    topic, topic_label, publish_date, fetched_date, push_date, is_pushed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article.nature_id,
                article.title,
                article.title_en,
                article.summary,
                article.source,
                getattr(article, 'source_short', None),
                article.authors,
                article.link,
                article.topic,
                article.topic_label,
                article.publish_date,
                article.fetched_date,
                article.push_date,
                1 if article.is_pushed else 0
            ))
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None  # 已存在
        except Exception as e:
            print(f"Insert article error: {e}")
            return None


def article_exists(nature_id: str) -> bool:
    """检查文章是否已存在"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM articles WHERE nature_id = ?", (nature_id,))
        return cursor.fetchone() is not None


def get_articles(
    date: Optional[str] = None,
    topic: Optional[str] = None,
    source: Optional[str] = None,  # 新增：来源筛选 (Nature / HBR / all)
    page: int = 1,
    page_size: int = 10
) -> tuple[List[Article], int]:
    """获取文章列表，支持分页和筛选"""
    with get_db() as conn:
        cursor = conn.cursor()

        # 构建查询条件
        conditions = []
        params = []

        if date:
            conditions.append("push_date LIKE ?")
            params.append(f"{date}%")

        if topic:
            conditions.append("topic = ?")
            params.append(topic)

        if source and source != "all":
            # 支持 source 或 source_short 筛选
            conditions.append("(source LIKE ? OR source_short = ?)")
            params.append(f"%{source}%")
            params.append(source)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 获取总数
        count_sql = f"SELECT COUNT(*) as count FROM articles WHERE {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()["count"]

        # 分页查询
        offset = (page - 1) * page_size
        query_sql = f"""
            SELECT * FROM articles
            WHERE {where_clause}
            ORDER BY COALESCE(push_date, publish_date, fetched_date) DESC, id DESC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])

        cursor.execute(query_sql, params)
        rows = cursor.fetchall()

        articles = [_row_to_article(row) for row in rows]
        return articles, total


def get_article_by_id(article_id: int) -> Optional[Article]:
    """根据ID获取文章"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        return _row_to_article(row) if row else None


def get_articles_by_date(date: str) -> List[Article]:
    """获取指定日期的所有文章"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM articles WHERE push_date LIKE ? ORDER BY id DESC",
            (f"{date}%",)
        )
        rows = cursor.fetchall()
        return [_row_to_article(row) for row in rows]


def get_unpushed_articles() -> List[Article]:
    """获取未推送的文章"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM articles WHERE is_pushed = 0 ORDER BY id ASC"
        )
        rows = cursor.fetchall()
        return [_row_to_article(row) for row in rows]


def mark_articles_pushed(article_ids: List[int], push_date: str):
    """标记文章已推送"""
    if not article_ids:
        return
    with get_db() as conn:
        cursor = conn.cursor()
        placeholders = ",".join(["?"] * len(article_ids))
        cursor.execute(
            f"UPDATE articles SET is_pushed = 1, push_date = ? WHERE id IN ({placeholders})",
            [push_date] + article_ids
        )


def mark_article_unpushed(article_id: int):
    """标记文章为未推送（用于重新推送）"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE articles SET is_pushed = 0, push_date = NULL WHERE id = ?",
            (article_id,)
        )


def get_article_by_nature_id(nature_id: str) -> Optional[Article]:
    """根据nature_id获取文章"""
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM articles WHERE nature_id = ?", (nature_id,))
        row = cursor.fetchone()
        return Article(**dict(row)) if row else None


def get_total_articles_count() -> int:
    """获取文章总数"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM articles")
        return cursor.fetchone()["count"]


def _row_to_article(row) -> Article:
    """将数据库行转换为Article对象"""
    def safe_get(row, key, default=None):
        try:
            return row[key]
        except (KeyError, IndexError):
            return default

    return Article(
        id=safe_get(row, "id"),
        nature_id=safe_get(row, "nature_id", ""),
        title=safe_get(row, "title", ""),
        title_en=safe_get(row, "title_en"),
        summary=safe_get(row, "summary", ""),
        source=safe_get(row, "source", ""),
        source_short=safe_get(row, "source_short"),
        authors=safe_get(row, "authors", ""),
        link=safe_get(row, "link", ""),
        topic=safe_get(row, "topic", ""),
        topic_label=safe_get(row, "topic_label", ""),
        publish_date=safe_get(row, "publish_date", ""),
        fetched_date=safe_get(row, "fetched_date", ""),
        push_date=safe_get(row, "push_date"),
        is_pushed=bool(safe_get(row, "is_pushed", 0)),
        created_at=safe_get(row, "created_at")
    )


# ========== 订阅者操作 ==========
def add_subscriber(email: str, interests: List[str] = None) -> Optional[int]:
    """添加订阅者"""
    import json
    with get_db() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO subscribers (email, interests, is_active, created_at)
                VALUES (?, ?, 1, ?)
            """, (email, json.dumps(interests or []), datetime.now().isoformat()))
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            # 已存在，更新
            cursor.execute("""
                UPDATE subscribers SET is_active = 1, interests = ?
                WHERE email = ?
            """, (json.dumps(interests or []), email))
            return cursor.fetchone()
        except Exception as e:
            print(f"Add subscriber error: {e}")
            return None


def remove_subscriber(email: str) -> bool:
    """取消订阅（软删除）"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE subscribers SET is_active = 0 WHERE email = ?",
            (email,)
        )
        return cursor.rowcount > 0


def get_active_subscribers() -> List[Subscriber]:
    """获取所有活跃订阅者"""
    import json
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM subscribers WHERE is_active = 1 ORDER BY created_at DESC"
        )
        rows = cursor.fetchall()
        result = []
        for row in rows:
            result.append(Subscriber(
                id=row["id"],
                email=row["email"],
                interests=json.loads(row["interests"]) if row["interests"] else [],
                is_active=bool(row["is_active"]),
                created_at=row["created_at"],
                last_push_at=row["last_push_at"]
            ))
        return result


def get_subscriber_count() -> int:
    """获取订阅者数量"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM subscribers WHERE is_active = 1")
        return cursor.fetchone()["count"]


def update_subscriber_last_push(email: str):
    """更新订阅者最后推送时间"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE subscribers SET last_push_at = ? WHERE email = ?",
            (datetime.now().isoformat(), email)
        )


# ========== 推送日志操作 ==========
def add_push_log(push_date: str, article_count: int, status: str = "pending",
                  error_message: str = None) -> int:
    """添加推送日志"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO push_logs (push_date, article_count, status, error_message)
            VALUES (?, ?, ?, ?)
        """, (push_date, article_count, status, error_message))
        return cursor.lastrowid


def update_push_log(log_id: int, success_count: int, failed_count: int, status: str,
                    error_message: str = None):
    """更新推送日志"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE push_logs
            SET success_count = ?, failed_count = ?, status = ?, error_message = ?
            WHERE id = ?
        """, (success_count, failed_count, status, error_message, log_id))


def get_last_push_log() -> Optional[PushLog]:
    """获取最近一次推送日志"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM push_logs ORDER BY created_at DESC LIMIT 1"
        )
        row = cursor.fetchone()
        return PushLog(
            id=row["id"],
            push_date=row["push_date"],
            article_count=row["article_count"],
            success_count=row["success_count"],
            failed_count=row["failed_count"],
            status=row["status"],
            error_message=row["error_message"] if row["error_message"] else None
        ) if row else None


# ========== 统计操作 ==========
def get_push_calendar(days: int = 30) -> List[dict]:
    """获取推送日历（最近N天的推送情况）"""
    from datetime import datetime, timedelta

    with get_db() as conn:
        cursor = conn.cursor()

        # 计算日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        cursor.execute("""
            SELECT push_date, COUNT(*) as article_count
            FROM articles
            WHERE push_date >= ? AND push_date < ?
            GROUP BY DATE(push_date)
            ORDER BY push_date DESC
        """, (start_date.isoformat(), end_date.isoformat()))

        rows = cursor.fetchall()

        # 构建结果，补充没有推送的日期
        result = []
        current = end_date
        weekday_names = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]

        date_count_map = {row["push_date"][:10]: row["article_count"] for row in rows}

        for _ in range(days):
            date_str = current.strftime("%Y-%m-%d")
            weekday = weekday_names[current.weekday()]
            result.append({
                "date": date_str,
                "article_count": date_count_map.get(date_str, 0),
                "weekday": weekday
            })
            current -= timedelta(days=1)

        return result


if __name__ == "__main__":
    init_database()
    print("数据库初始化完成！")
