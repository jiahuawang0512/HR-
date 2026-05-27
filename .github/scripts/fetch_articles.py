#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, 'backend')

import config
from scraper import fetch_daily_articles
from scraper_hbr_cn import HBRCaiJingScraper

print('开始抓取文章...')

# 抓取 Nature
try:
    articles, total = fetch_daily_articles()
    print(f'✅ Nature 抓取完成: {total} 篇')
except Exception as e:
    print(f'⚠️  Nature 抓取失败: {e}')

# 抓取 HBR 中文版
try:
    scraper = HBRCaiJingScraper()
    cn_articles = scraper.fetch_articles()
    print(f'✅ HBR 中文版抓取完成: {len(cn_articles)} 篇')
except Exception as e:
    print(f'⚠️  HBR 中文版抓取失败: {e}')

print('抓取完成!')
