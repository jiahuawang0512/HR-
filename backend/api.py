# HR信息日报 - API 路由模块

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    Article, ArticleResponse, ArticleListResponse,
    SubscribeRequest, SubscribeResponse,
    PushCalendarResponse, PushCalendarItem,
    SystemStatusResponse, SystemStatus,
    FetchResponse,
    TopicsResponse, TopicItem,
    Subscriber
)
from database import (
    get_articles, get_article_by_id, get_articles_by_date,
    add_subscriber, remove_subscriber, get_active_subscribers,
    get_push_calendar, get_total_articles_count, get_subscriber_count,
    get_last_push_log, init_database
)
from scheduler import (
    get_scheduler_status, trigger_fetch_now, trigger_push_now,
    get_next_push_time, start_scheduler
)
import config


# 创建路由
router = APIRouter(prefix="")


# ========== 领域分类映射 ==========
TOPICS = [
    {"value": "recruitment", "label": "招聘与选拔"},
    {"value": "training", "label": "培训与发展"},
    {"value": "performance", "label": "绩效管理"},
    {"value": "compensation", "label": "薪酬福利"},
    {"value": "employee-relations", "label": "员工关系"},
    {"value": "hr-tech", "label": "HR科技与AI"},
    {"value": "organizational-behavior", "label": "组织行为学"},
    {"value": "diversity", "label": "多元化与包容性"},
]


# ========== 来源分类映射 ==========
SOURCES = [
    {"value": "all", "label": "全部来源"},
    {"value": "Nature", "label": "Nature"},
    {"value": "HBR", "label": "哈佛商业评论中文版"},
]


# ========== 文章接口 ==========
@router.get("/articles")
async def list_articles(
    date: Optional[str] = Query(None, description="筛选日期 YYYY-MM-DD"),
    topic: Optional[str] = Query(None, description="筛选领域"),
    source: Optional[str] = Query("all", description="筛选来源 (Nature/HBR/all)"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量")
):
    """获取文章列表"""
    articles, total = get_articles(date=date, topic=topic, source=source, page=page, page_size=page_size)

    return ArticleListResponse(
        code=200,
        data={
            "total": total,
            "page": page,
            "page_size": page_size,
            "source": source,
            "articles": [
                {
                    **article.model_dump(),
                    "summary": article.summary[:150] + "..." if len(article.summary) > 150 else article.summary
                }
                for article in articles
            ]
        }
    )


@router.get("/articles/{article_id}")
async def get_article(article_id: int):
    """获取单篇文章详情"""
    article = get_article_by_id(article_id)

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    return ArticleResponse(code=200, data=article)


@router.get("/articles-date/{date}")
async def get_articles_by_date_route(date: str):
    """获取指定日期的所有文章"""
    articles = get_articles_by_date(date)

    return ArticleListResponse(
        code=200,
        data={
            "total": len(articles),
            "date": date,
            "articles": articles
        }
    )


# ========== 订阅接口 ==========
@router.post("/subscribe", response_model=SubscribeResponse)
async def subscribe(request: SubscribeRequest):
    """订阅推送"""
    # 验证邮箱格式
    if "@" not in request.email or "." not in request.email.split("@")[-1]:
        return SubscribeResponse(code=400, message="邮箱格式不正确")

    # 验证领域
    valid_topics = [t["value"] for t in TOPICS]
    interests = [t for t in request.interests if t in valid_topics]

    # 添加订阅者
    result = add_subscriber(request.email, interests)

    if result:
        return SubscribeResponse(code=200, message="订阅成功")
    else:
        return SubscribeResponse(code=500, message="订阅失败，请稍后重试")


@router.post("/unsubscribe", response_model=SubscribeResponse)
async def unsubscribe(email: str = Query(..., description="邮箱地址")):
    """取消订阅"""
    success = remove_subscriber(email)

    if success:
        return SubscribeResponse(code=200, message="已取消订阅")
    else:
        return SubscribeResponse(code=404, message="未找到该订阅者")


@router.get("/subscribers/count")
async def get_subscribers_count():
    """获取订阅者数量"""
    count = get_subscriber_count()
    return {"code": 200, "data": {"count": count}}


# ========== 日历和统计接口 ==========
@router.get("/push-calendar", response_model=PushCalendarResponse)
async def get_push_calendar(days: int = Query(30, ge=7, le=365)):
    """获取推送日历"""
    calendar_data = get_push_calendar(days)

    return PushCalendarResponse(
        code=200,
        data=[PushCalendarItem(**item) for item in calendar_data]
    )


@router.get("/topics", response_model=TopicsResponse)
async def get_topics():
    """获取所有领域分类"""
    return TopicsResponse(
        code=200,
        data=[TopicItem(**t) for t in TOPICS]
    )


@router.get("/sources")
async def get_sources():
    """获取所有来源分类"""
    return {
        "code": 200,
        "data": SOURCES
    }


@router.get("/stats")
async def get_stats():
    """获取统计数据"""
    total_articles = get_total_articles_count()
    total_subscribers = get_subscriber_count()

    return {
        "code": 200,
        "data": {
            "total_articles": total_articles,
            "total_subscribers": total_subscribers
        }
    }


# ========== 管理接口 ==========
@router.get("/admin/status", response_model=SystemStatusResponse)
async def get_system_status():
    """获取系统状态"""
    status = get_scheduler_status()

    return SystemStatusResponse(
        code=200,
        data=SystemStatus(
            total_articles=get_total_articles_count(),
            total_subscribers=get_subscriber_count(),
            last_fetch=status.get("last_fetch"),
            last_push=status.get("last_push"),
            next_push=status.get("next_push") or "未设置",
            scheduler_running=status.get("running", False)
        )
    )


@router.post("/admin/fetch", response_model=FetchResponse)
async def manual_fetch():
    """手动触发抓取（管理员）"""
    try:
        result = trigger_fetch_now()

        if "error" in result:
            return FetchResponse(
                code=500,
                message=f"抓取失败: {result['error']}",
                data=result
            )

        return FetchResponse(
            code=200,
            message="抓取成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/push", response_model=FetchResponse)
async def manual_push():
    """手动触发推送（管理员）"""
    try:
        trigger_push_now()

        return FetchResponse(
            code=200,
            message="推送完成",
            data={}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ========== 健康检查 ==========
@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "code": 200,
        "message": "服务正常",
        "timestamp": datetime.now().isoformat()
    }
