#!/usr/bin/env python3
import sys
import os
from datetime import datetime

sys.path.insert(0, 'backend')

import config
from database import init_database, insert_article
from models import Article
from scraper import fetch_daily_articles
from scraper_hbr_cn import HBRCaiJingScraper

print('开始抓取文章...')

# 初始化数据库
init_database()

# 抓取 Nature
try:
    articles, total = fetch_daily_articles()
    print(f'✅ Nature 抓取完成: {total} 篇')
    
    # 保存到数据库
    saved = 0
    for article_data in articles:
        article = Article(
            nature_id=article_data.get('nature_id', article_data.get('link', '')),
            title=article_data['title'],
            title_en=article_data.get('title_en', ''),
            summary=article_data.get('summary', article_data['title']),
            source=article_data.get('source', 'Nature'),
            source_short=article_data.get('source_short', 'Nature'),
            authors=article_data.get('authors', ''),
            link=article_data['link'],
            topic=article_data.get('topic', 'general'),
            topic_label=article_data.get('topic_label', '其他'),
            publish_date=article_data.get('publish_date', datetime.now().strftime('%Y-%m-%d')),
            fetched_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            push_date=datetime.now().strftime('%Y-%m-%d'),
            is_pushed=True
        )
        result = insert_article(article)
        if result:
            saved += 1
    print(f'   保存到数据库: {saved} 篇')
except Exception as e:
    print(f'⚠️  Nature 抓取失败: {e}')

# 抓取 HBR 中文版
try:
    scraper = HBRCaiJingScraper()
    cn_articles = scraper.fetch_articles()
    print(f'✅ HBR 中文版抓取完成: {len(cn_articles)} 篇')
    
    # 保存到数据库
    saved = 0
    for article_data in cn_articles:
        article = Article(
            nature_id=article_data.get('id', article_data.get('link', '')),
            title=article_data['title'],
            title_en='',
            summary=article_data.get('summary', article_data['title']),
            source='哈佛商业评论中文版',
            source_short='HBR CN',
            authors=article_data.get('authors', ''),
            link=article_data['link'],
            topic=article_data.get('topic', 'general'),
            topic_label=article_data.get('topic_label', '其他'),
            publish_date=article_data.get('publish_date', datetime.now().strftime('%Y-%m-%d')),
            fetched_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            push_date=datetime.now().strftime('%Y-%m-%d'),
            is_pushed=True
        )
        result = insert_article(article)
        if result:
            saved += 1
    print(f'   保存到数据库: {saved} 篇')
except Exception as e:
    print(f'⚠️  HBR 中文版抓取失败: {e}')

print('抓取完成!')
