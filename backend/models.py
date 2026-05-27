# HR信息日报 - 数据模型

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


# ========== 文章模型 ==========
class ArticleBase(BaseModel):
    nature_id: str
    title: str
    title_en: Optional[str] = None
    summary: str
    source: str
    source_short: Optional[str] = None  # 来源简称：Nature / HBR
    authors: str
    link: str
    topic: str
    topic_label: str
    publish_date: str


class ArticleCreate(ArticleBase):
    pass


class Article(ArticleBase):
    id: Optional[int] = None
    fetched_date: str
    push_date: Optional[str] = None
    is_pushed: bool = False
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# ========== 订阅者模型 ==========
class SubscriberBase(BaseModel):
    email: str
    interests: List[str] = []


class SubscriberCreate(SubscriberBase):
    pass


class Subscriber(SubscriberBase):
    id: int
    is_active: bool = True
    created_at: str
    last_push_at: Optional[str] = None

    class Config:
        from_attributes = True


# ========== 推送日志模型 ==========
class PushLogBase(BaseModel):
    push_date: str
    article_count: int
    success_count: int = 0
    failed_count: int = 0
    status: str = "pending"
    error_message: Optional[str] = None


class PushLog(PushLogBase):
    id: int

    class Config:
        from_attributes = True


# ========== API 请求/响应模型 ==========
class SubscribeRequest(BaseModel):
    email: str
    interests: List[str] = []


class SubscribeResponse(BaseModel):
    code: int
    message: str


class ArticleListResponse(BaseModel):
    code: int
    data: dict


class ArticleResponse(BaseModel):
    code: int
    data: Article


class PushCalendarItem(BaseModel):
    date: str
    article_count: int
    weekday: str


class PushCalendarResponse(BaseModel):
    code: int
    data: List[PushCalendarItem]


class SystemStatus(BaseModel):
    total_articles: int
    total_subscribers: int
    last_fetch: Optional[str]
    last_push: Optional[str]
    next_push: str
    scheduler_running: bool


class SystemStatusResponse(BaseModel):
    code: int
    data: SystemStatus


class FetchResponse(BaseModel):
    code: int
    message: str
    data: dict


class TopicItem(BaseModel):
    value: str
    label: str


class TopicsResponse(BaseModel):
    code: int
    data: List[TopicItem]


class ErrorResponse(BaseModel):
    code: int
    message: str
