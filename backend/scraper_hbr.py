# HR信息日报 - 哈佛商业评论 (HBR) 文章抓取模块

import re
import time
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from bs4 import BeautifulSoup

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config


# User-Agent 池
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class HBRScraper:
    """哈佛商业评论 (HBR) 文章抓取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })
        self.base_url = "https://hbr.org"
        self.topic_mapping = self._build_topic_mapping()

    def _build_topic_mapping(self) -> dict:
        """构建关键词到分类的映射"""
        return {
            "recruitment": {
                "label": "招聘与选拔",
                "keywords": ["recruitment", "hiring", "talent acquisition", "candidate", "selection", "interview", "hiring", "recruit"]
            },
            "training": {
                "label": "培训与发展",
                "keywords": ["training", "development", "learning", "mentoring", "coaching", "education", "upskill", "reskill"]
            },
            "performance": {
                "label": "绩效管理",
                "keywords": ["performance", "KPI", "OKR", "appraisal", "evaluation", "productivity", "feedback"]
            },
            "compensation": {
                "label": "薪酬福利",
                "keywords": ["compensation", "salary", "pay", "benefits", "reward", "incentive", "bonus", "pay equity"]
            },
            "employee-relations": {
                "label": "员工关系",
                "keywords": ["employee", "workplace", "engagement", "satisfaction", "retention", "turnover", "burnout", "work-life", "well-being", "mental health"]
            },
            "hr-tech": {
                "label": "HR科技与AI",
                "keywords": ["AI", "artificial intelligence", "machine learning", "algorithm", "digital", "automation", "HR tech", "generative AI", "ChatGPT"]
            },
            "organizational-behavior": {
                "label": "组织行为学",
                "keywords": ["organizational", "leadership", "culture", "behavior", "team", "collaboration", "innovation", "change management"]
            },
            "diversity": {
                "label": "多元化与包容性",
                "keywords": ["diversity", "inclusion", "equity", "bias", "discrimination", "gender", "equality", "belonging"]
            }
        }

    def _classify_topic(self, title: str, summary: str) -> Tuple[str, str]:
        """根据标题和摘要分类文章"""
        text = (title + " " + summary).lower()

        best_topic = "hr-tech"
        best_score = 0

        for topic, info in self.topic_mapping.items():
            score = sum(1 for keyword in info["keywords"] if keyword in text)
            for keyword in info["keywords"]:
                if keyword in title.lower():
                    score += 2

            if score > best_score:
                best_score = score
                best_topic = topic

        return best_topic, self.topic_mapping[best_topic]["label"]

    def _get_random_headers(self) -> dict:
        """获取随机请求头"""
        import random
        return {
            "User-Agent": random.choice(USER_AGENTS)
        }

    def fetch_topic_page(self, topic: str, max_pages: int = 3) -> List[dict]:
        """抓取单个话题页面的文章"""
        results = []
        topic_url = f"{self.base_url}/topic/{topic}"

        for page in range(1, max_pages + 1):
            try:
                params = {"page": page} if page > 1 else {}
                response = self.session.get(
                    topic_url,
                    params=params,
                    headers=self._get_random_headers(),
                    timeout=30
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "lxml")
                    articles = self._parse_article_list(soup)
                    results.extend(articles)
                    print(f"  [{topic}] 第{page}页: 抓取到 {len(articles)} 条")
                else:
                    print(f"  [{topic}] 请求失败: {response.status_code}")
                    break

                time.sleep(2)  # 避免请求过快

            except Exception as e:
                print(f"  [{topic}] 抓取异常: {e}")
                continue

        return results

    def fetch_search_results(self, keyword: str, max_results: int = 20) -> List[dict]:
        """通过搜索抓取文章"""
        results = []
        search_url = f"{self.base_url}/search"

        params = {
            "q": keyword,
            "type": "article"
        }

        try:
            response = self.session.get(
                search_url,
                params=params,
                headers=self._get_random_headers(),
                timeout=30
            )

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "lxml")
                articles = self._parse_article_list(soup)
                results.extend(articles)
                print(f"  [搜索 {keyword}] 抓取到 {len(articles)} 条")
            else:
                print(f"  [搜索 {keyword}] 请求失败: {response.status_code}")

        except Exception as e:
            print(f"  [搜索 {keyword}] 抓取异常: {e}")

        time.sleep(2)
        return results

    def _parse_article_list(self, soup: BeautifulSoup) -> List[dict]:
        """解析文章列表页面"""
        articles = []

        # 尝试多种选择器
        article_elements = (
            soup.select(".stream-item") or
            soup.select(".topic-stream-item") or
            soup.select("article") or
            soup.select(".content-card") or
            soup.select(".hBRXjd")  # HBR 常用的文章卡片类名
        )

        for elem in article_elements:
            try:
                # 提取标题和链接
                title_elem = (
                    elem.select_one("h3 a") or
                    elem.select_one("h2 a") or
                    elem.select_one("a[href*='/']") or
                    elem.select_one(".article-title a")
                )

                if not title_elem:
                    continue

                href = title_elem.get("href", "")
                if not href or href.startswith("#"):
                    continue

                # 确保是完整 URL
                if href.startswith("/"):
                    link = f"{self.base_url}{href}"
                else:
                    link = href

                # 提取 article slug 作为 ID
                match = re.search(r'/(\d{4})/(\d{2})/([a-zA-Z0-9_-]+)', href)
                if match:
                    hbr_id = match.group(3)
                else:
                    hbr_id = re.sub(r'[^a-zA-Z0-9]', '-', title_elem.get_text(strip=True).lower()[:50])

                title = title_elem.get_text(strip=True)

                # 提取作者
                author_elem = (
                    elem.select_one(".byline") or
                    elem.select_one(".author") or
                    elem.select_one("[class*='author']")
                )
                authors = author_elem.get_text(strip=True) if author_elem else "Harvard Business Review"

                # 提取发布日期
                date_elem = (
                    elem.select_one("time") or
                    elem.select_one(".dateline") or
                    elem.select_one("[class*='date']")
                )
                date_str = date_elem.get_text(strip=True) if date_elem else ""
                publish_date = self._parse_date(date_str)

                # 提取摘要/描述
                summary_elem = (
                    elem.select_one(".description") or
                    elem.select_one(".summary") or
                    elem.select_one(".excerpt") or
                    elem.select_one("[class*='description']")
                )
                summary = summary_elem.get_text(strip=True) if summary_elem else ""

                # 分类
                topic, topic_label = self._classify_topic(title, summary)

                articles.append({
                    "hbr_id": hbr_id,
                    "nature_id": hbr_id,  # 兼容 scheduler.py 中的字段名
                    "title": self._translate_title(title),
                    "title_en": title,
                    "summary": summary or self._generate_summary(title, topic),
                    "source": "Harvard Business Review",
                    "source_short": "HBR",
                    "authors": authors,
                    "link": link,
                    "topic": topic,
                    "topic_label": topic_label,
                    "publish_date": publish_date
                })

            except Exception as e:
                continue

        return articles

    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        # HBR 常用格式
        date_formats = [
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
            "%Y-%m-%d",
            "%B %d, %Y"
        ]

        date_str = date_str.strip()

        # 移除 "on" 前缀等
        date_str = re.sub(r'^on\s+', '', date_str)

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue

        # 尝试提取日期部分
        match = re.search(r'(\d{4})/(\d{2})/', date_str)
        if match:
            return f"{match.group(1)}-{match.group(2)}-01"

        return datetime.now().strftime("%Y-%m-%d")

    def _translate_title(self, title: str) -> str:
        """HBR 标题通常为英文，保留原文"""
        return title

    def _generate_summary(self, title: str, topic: str) -> str:
        """生成简要说明"""
        topic_summaries = {
            "recruitment": "本文探讨了招聘与人才选拔领域的管理实践，分享了提升招聘效果和人才质量的策略建议。",
            "training": "本文聚焦于员工培训与职业发展，分享了促进组织学习和人才成长的实践经验。",
            "performance": "本文围绕绩效管理与评估展开，提供了优化绩效管理体系的专业建议。",
            "compensation": "文章讨论了薪酬福利与激励机制的设计问题，揭示了激励策略对组织效能的影响。",
            "employee-relations": "本文关注员工关系与工作体验，对提升员工敬业度和组织承诺具有实践意义。",
            "hr-tech": "本文探讨了人工智能与数字化技术在企业管理中的应用，分析了技术变革对组织的深远影响。",
            "organizational-behavior": "研究围绕组织行为与领导力展开，为提升团队协作和管理效能提供了洞见。",
            "diversity": "本文关注职场多元化和包容性议题，对促进公平就业和组织可持续发展具有重要启示。"
        }
        return topic_summaries.get(topic, "本文探讨了管理领域的重要议题，提供了有价值的管理洞见和实践建议。")

    def fetch_all_articles(self) -> Tuple[List[dict], int]:
        """抓取所有 HR 相关话题的最新文章"""
        all_articles = []
        seen_ids = set()

        # HR 相关的话题
        hr_topics = [
            "leadership",           # 领导力
            "managing-teams",       # 团队管理
            "managing-yourself",    # 自我管理
            "human-resources",      # 人力资源
            "employee-engagement",  # 员工敬业度
            "organizational-change", # 组织变革
            "diversity",            # 多元化
            "career-transitions",   # 职业发展
        ]

        print("\n开始抓取 HBR 管理相关文章...")
        print("=" * 50)

        for topic in hr_topics:
            print(f"\n正在抓取话题: {topic}")
            articles = self.fetch_topic_page(topic, max_pages=2)

            for article in articles:
                if article["hbr_id"] not in seen_ids:
                    seen_ids.add(article["hbr_id"])
                    all_articles.append(article)

            time.sleep(1)

        # 按发布日期排序
        all_articles.sort(key=lambda x: x["publish_date"], reverse=True)

        print("\n" + "=" * 50)
        print(f"总共抓取到 {len(all_articles)} 篇文章（去重后）")

        return all_articles, len(all_articles)


def fetch_hbr_articles() -> Tuple[List[dict], int]:
    """抓取 HBR 文章主函数"""
    scraper = HBRScraper()
    articles, total = scraper.fetch_all_articles()
    return articles, total


if __name__ == "__main__":
    # 测试抓取
    articles, total = fetch_hbr_articles()
    print(f"\n抓取完成，共 {total} 篇文章")
    for i, article in enumerate(articles[:5], 1):
        print(f"\n--- 文章 {i} ---")
        print(f"标题: {article['title']}")
        print(f"来源: {article['source']}")
        print(f"作者: {article['authors']}")
        print(f"链接: {article['link']}")
        print(f"分类: {article['topic_label']}")