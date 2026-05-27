# HR信息日报 - 定时任务调度模块

import asyncio
import threading
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from database import (
    init_database, get_articles, get_articles_by_date,
    get_unpushed_articles, mark_articles_pushed,
    get_active_subscribers, add_push_log, update_push_log,
    get_total_articles_count, get_subscriber_count,
    get_last_push_log, update_subscriber_last_push
)
# 同时使用 HBR 和 Nature 作为数据源
from scraper_hbr_cn import HBRCaiJingScraper
from scraper import fetch_daily_articles as fetch_nature_articles
from pusher import push_daily


# 全局调度器实例
_scheduler = None
_scheduler_lock = threading.Lock()


def job_fetch_articles():
    """定时抓取任务 - 从 HBR (英文版 + 中文版) 抓取 HR 相关文章"""
    print("\n" + "=" * 50)
    print(f"⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行文章抓取任务...")
    print("=" * 50)

    try:
        all_articles = []
        seen_ids = set()

        # 1. 抓取 Nature 期刊（数据源之一）
        print("\n开始抓取 Nature 期刊 HR 相关文章...")
        try:
            nature_articles, nature_total = fetch_nature_articles()
            for article in nature_articles:
                if article.get("nature_id") not in seen_ids:
                    seen_ids.add(article.get("nature_id"))
                    all_articles.append(article)
            print(f"✅ Nature 期刊抓取完成，共 {nature_total} 篇")
        except Exception as e:
            print(f"⚠️  Nature 期刊抓取失败: {e}")

        # 2. 抓取 HBR 中文版（补充数据源）
        print("\n开始抓取 HBR 中文版文章...")
        try:
            cn_scraper = HBRCaiJingScraper()
            cn_articles = cn_scraper.fetch_articles()
            for article in cn_articles:
                if article.get("nature_id") not in seen_ids:
                    seen_ids.add(article.get("nature_id"))
                    all_articles.append(article)
            print(f"✅ HBR 中文版抓取完成，共 {len(cn_articles)} 篇")
        except Exception as e:
            print(f"⚠️  HBR 中文版抓取失败: {e}")

        # 3. 抓取其他 HR 相关数据源（未来可扩展）
        # 例如：SHRM、Academy of Management、Journal of Applied Psychology 等
        print("\n✅ 所有数据源抓取完成")

        if not all_articles:
            print("⚠️  未抓取到任何文章")
            return {"fetched": 0, "new": 0, "error": "No articles fetched"}

        # 按发布日期排序（最新的在前）
        all_articles.sort(key=lambda x: x.get("publish_date", ""), reverse=True)

        # 优先使用昨天的文章，如果没有则使用最近的文章
        from datetime import timedelta
        yesterday = (datetime.now() - timedelta(days=config.FETCH_DAYS_AGO)).strftime("%Y-%m-%d")
        yesterday_articles = [a for a in all_articles if a.get("publish_date") == yesterday]

        if yesterday_articles:
            print(f"\n✅ 找到 {len(yesterday_articles)} 篇昨天发布的文章")
            articles_to_use = yesterday_articles
        else:
            print(f"\n⚠️  未找到昨天发布的文章，使用最近的 {min(10, len(all_articles))} 篇文章")
            articles_to_use = all_articles[:10]  # 使用前10篇最新文章

        from models import Article

        new_count = 0
        pushed_count = 0
        today = datetime.now().strftime("%Y-%m-%d")

        # 用于存储所有需要推送的文章ID
        article_ids_to_push = []

        for article_data in articles_to_use:
            nature_id = article_data.get("nature_id", "")
            
            # 使用 database 模块的函数
            from database import insert_article, article_exists, get_article_by_nature_id

            if not article_exists(nature_id):
                # 新文章：插入数据库
                article = Article(
                    nature_id=nature_id,
                    title=article_data.get("title", ""),
                    title_en=article_data.get("title_en"),
                    summary=article_data.get("summary", ""),
                    source=article_data.get("source", "HBR"),
                    authors=article_data.get("authors", ""),
                    link=article_data.get("link", ""),
                    topic=article_data.get("topic", "hr-tech"),
                    topic_label=article_data.get("topic_label", "HR科技与AI"),
                    publish_date=article_data.get("publish_date", today),
                    fetched_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    push_date=today,
                    is_pushed=False
                )
                result = insert_article(article)
                if result:
                    new_count += 1
                    # 获取新插入文章的ID
                    new_article = get_article_by_nature_id(nature_id)
                    if new_article:
                        article_ids_to_push.append(new_article.id)
            else:
                # 已存在的文章：标记为未推送，以便今天再次推送
                existing_article = get_article_by_nature_id(nature_id)
                if existing_article and existing_article.is_pushed:
                    # 标记为未推送
                    from database import mark_article_unpushed
                    mark_article_unpushed(existing_article.id)
                    article_ids_to_push.append(existing_article.id)
                elif existing_article:
                    article_ids_to_push.append(existing_article.id)

        # 获取所有未推送的文章
        from database import get_unpushed_articles
        unpushed = get_unpushed_articles()

        # 标记为已推送
        if unpushed:
            article_ids = [a.id for a in unpushed]
            from database import mark_articles_pushed
            mark_articles_pushed(article_ids, today)
            pushed_count = len(unpushed)

        print(f"\n✅ 抓取完成！")
        print(f"   本次新增: {new_count} 篇")
        print(f"   今日推送: {pushed_count} 篇")

        return {"fetched": len(articles_to_use), "new": new_count, "pushed": pushed_count}

    except Exception as e:
        print(f"\n❌ 抓取任务失败: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


def job_push_daily():
    """定时推送任务"""
    print("\n" + "=" * 50)
    print(f"📬 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始执行每日推送任务...")
    print("=" * 50)

    try:
        today = datetime.now().strftime("%Y-%m-%d")

        # 获取今日文章
        articles = get_articles_by_date(today)

        if not articles:
            print("⚠️  今日没有文章可推送，尝试抓取...")
            fetch_result = job_fetch_articles()
            if "error" in fetch_result:
                print("抓取失败，跳过推送")
                return
            articles = get_articles_by_date(today)

        if not articles:
            print("⚠️  仍然没有文章可推送，跳过本次推送")
            return

        # 获取订阅者
        subscribers = get_active_subscribers()

        if not subscribers:
            print("⚠️  没有活跃订阅者，跳过推送")
            return

        # 转换为字典列表
        subscriber_dicts = [
            {"email": s.email, "interests": s.interests}
            for s in subscribers
        ]

        # 添加推送日志
        log_id = add_push_log(today, len(articles), status="running")

        # 执行推送
        results = push_daily(articles, subscriber_dicts, today)

        # 更新推送日志
        status = "success" if results["failed"] == 0 else "partial" if results["success"] > 0 else "failed"
        error_msg = "; ".join(results["errors"]) if results["errors"] else None

        update_push_log(log_id, results["success"], results["failed"], status, error_msg)

        # 更新订阅者最后推送时间
        for subscriber in subscriber_dicts:
            update_subscriber_last_push(subscriber["email"])

        print(f"\n📤 推送完成！")
        print(f"   订阅者总数: {results['total']}")
        print(f"   成功发送: {results['success']}")
        print(f"   发送失败: {results['failed']}")

        if results["errors"]:
            print(f"   错误详情:")
            for err in results["errors"][:5]:  # 只显示前5个错误
                print(f"     - {err}")

    except Exception as e:
        print(f"\n❌ 推送任务失败: {e}")
        import traceback
        traceback.print_exc()


def init_scheduler() -> BackgroundScheduler:
    """初始化定时任务调度器"""
    global _scheduler

    with _scheduler_lock:
        if _scheduler is not None:
            return _scheduler

        # 创建调度器
        _scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

        # 添加抓取任务 (每天 11:50)
        _scheduler.add_job(
            job_fetch_articles,
            CronTrigger(
                hour=config.FETCH_CRON_HOUR,
                minute=config.FETCH_CRON_MINUTE,
                timezone="Asia/Shanghai"
            ),
            id="fetch_articles",
            name="每日文章抓取",
            replace_existing=True
        )

        # 添加推送任务 (每天 12:00)
        _scheduler.add_job(
            job_push_daily,
            CronTrigger(
                hour=config.PUSH_CRON_HOUR,
                minute=config.PUSH_CRON_MINUTE,
                timezone="Asia/Shanghai"
            ),
            id="push_daily",
            name="每日推送",
            replace_existing=True
        )

        return _scheduler


def start_scheduler():
    """启动调度器"""
    scheduler = init_scheduler()

    if not scheduler.running:
        scheduler.start()
        print("\n✅ 定时任务调度器已启动")
        print(f"   抓取时间: 每天 {config.FETCH_CRON_HOUR}:{config.FETCH_CRON_MINUTE:02d}")
        print(f"   推送时间: 每天 {config.PUSH_CRON_HOUR}:{config.PUSH_CRON_MINUTE:02d}")
    else:
        print("调度器已在运行中")

    return scheduler


def stop_scheduler():
    """停止调度器"""
    global _scheduler

    with _scheduler_lock:
        if _scheduler is not None and _scheduler.running:
            _scheduler.shutdown(wait=False)
            _scheduler = None
            print("调度器已停止")


def get_next_push_time() -> str:
    """获取下次推送时间"""
    global _scheduler

    if _scheduler is None or not _scheduler.running:
        return "调度器未运行"

    job = _scheduler.get_job("push_daily")
    if job is None:
        return "未设置推送任务"

    next_run = job.next_run_time
    if next_run is None:
        return "无下次执行时间"

    return next_run.strftime("%Y-%m-%d %H:%M:%S")


def get_scheduler_status() -> dict:
    """获取调度器状态"""
    global _scheduler

    running = _scheduler is not None and _scheduler.running

    # 获取下次推送时间
    next_push = get_next_push_time() if running else None

    # 获取最近抓取和推送时间
    last_fetch = None
    last_push = None

    last_push_log = get_last_push_log()
    if last_push_log:
        last_push = last_push_log.push_date

    return {
        "running": running,
        "next_push": next_push,
        "last_fetch": last_fetch,
        "last_push": last_push,
        "jobs": [
            {"id": job.id, "name": job.name, "next_run": job.next_run_time.strftime("%Y-%m-%d %H:%M") if job.next_run_time else None}
            for job in (_scheduler.get_jobs() if _scheduler else [])
        ]
    }


def trigger_fetch_now():
    """手动立即触发抓取"""
    return job_fetch_articles()


def trigger_push_now():
    """手动立即触发推送"""
    return job_push_daily()


if __name__ == "__main__":
    # 初始化数据库
    init_database()

    # 启动调度器
    scheduler = start_scheduler()

    # 保持运行
    try:
        while True:
            import time
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n正在停止调度器...")
        stop_scheduler()
