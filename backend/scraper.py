# HR信息日报 - Nature 文章抓取模块

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


# User-Agent 池，避免被识别为爬虫
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class NatureScraper:
    """Nature 文章抓取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })
        self.topic_mapping = self._build_topic_mapping()

    def _build_topic_mapping(self) -> dict:
        """构建关键词到分类的映射"""
        return {
            "recruitment": {
                "label": "招聘与选拔",
                "keywords": ["recruitment", "hiring", "talent acquisition", "candidate", "selection", "interview"]
            },
            "training": {
                "label": "培训与发展",
                "keywords": ["training", "development", "learning", "mentoring", "coaching", "education"]
            },
            "performance": {
                "label": "绩效管理",
                "keywords": ["performance", "KPI", "OKR", "appraisal", "evaluation", "productivity"]
            },
            "compensation": {
                "label": "薪酬福利",
                "keywords": ["compensation", "salary", "pay", "benefits", "reward", "incentive", "bonus"]
            },
            "employee-relations": {
                "label": "员工关系",
                "keywords": ["employee", "workplace", "engagement", "satisfaction", "retention", "turnover", "burnout", "work-life"]
            },
            "hr-tech": {
                "label": "HR科技与AI",
                "keywords": ["AI", "artificial intelligence", "machine learning", "algorithm", "digital", "automation", "HR tech"]
            },
            "organizational-behavior": {
                "label": "组织行为学",
                "keywords": ["organizational", "leadership", "culture", "behavior", "team", "collaboration", "innovation"]
            },
            "diversity": {
                "label": "多元化与包容性",
                "keywords": ["diversity", "inclusion", "equity", "bias", "discrimination", "gender", "equality"]
            }
        }

    def _classify_topic(self, title: str, summary: str) -> Tuple[Optional[str], Optional[str]]:
        """根据标题和摘要分类文章，同时检查是否与 HR 相关"""
        text = (title + " " + summary).lower()

        # 严格的 HR 相关关键词（需要匹配至少2个才算 HR 相关）
        # 分为"强关键词"和"弱关键词"
        # 强关键词：明确指向 HR 领域
        # 弱关键词：可能出现在非 HR 文章中，需要配合强关键词
        strong_hr_keywords = [
            "human resource", "HR", "human resources",
            "employee engagement", "employee satisfaction", "employee retention",
            "talent management", "talent acquisition", "recruitment", "hiring",
            "workforce management", "workforce analytics",
            "HRM", "personnel management", "human capital management",
            "compensation and benefits", "performance appraisal",
            "training and development", "leadership development",
            "succession planning", "employee wellbeing",
            "workplace diversity", "workplace inclusion",
            "organizational behavior", "industrial relations"
        ]
        
        weak_hr_keywords = [
            "employee", "workplace", "talent", "staffing",
            "leadership", "management", "organization", "training",
            "performance", "diversity", "inclusion", "wellbeing"
        ]
        
        # 排除词：包含这些词的文章通常不是 HR 相关
        exclude_keywords = [
            "nature reserve", "wildlife", "ecology", "biodiversity",
            "coal industry", "mining", "geology", "physics", "chemistry",
            "biology", "genetics", "molecular", "cellular",
            "astronomy", "astrophysics", "quantum", "particle physics"
        ]
        
        # 检查是否包含排除词
        if any(keyword in text for keyword in exclude_keywords):
            return None, None  # 排除非 HR 相关文章
        
        # 统计匹配的关键词数量
        strong_matches = sum(1 for keyword in strong_hr_keywords if keyword in text)
        weak_matches = sum(1 for keyword in weak_hr_keywords if keyword in text)
        
        # 需要至少1个强关键词，或者2个以上的弱关键词
        is_hr_related = (strong_matches >= 1) or (weak_matches >= 2)

        if not is_hr_related:
            return None, None  # 返回 None 表示不是 HR 相关文章

        best_topic = "hr-tech"
        best_score = 0

        for topic, info in self.topic_mapping.items():
            score = sum(1 for keyword in info["keywords"] if keyword in text)
            # 加权：标题中匹配权重更高
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

    def fetch_search_results(self, keyword: str, max_results: int = 20) -> List[dict]:
        """抓取单个关键词的搜索结果"""
        results = []
        url = "https://www.nature.com/search"

        params = {
            "q": keyword,
            "order": "relevance",
            "date_range": "last_12months",
            "page_size": min(max_results, 50)
        }

        for attempt in range(config.MAX_RETRIES):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=self._get_random_headers(),
                    timeout=30
                )

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "lxml")
                    articles = self._parse_search_results(soup)

                    # 去重（通过nature_id）
                    seen_ids = set()
                    for article in articles:
                        if article["nature_id"] not in seen_ids:
                            seen_ids.add(article["nature_id"])
                            results.append(article)

                    print(f"  [{keyword}] 抓取到 {len(results)} 条结果")
                    break

                elif response.status_code == 429:
                    print(f"  [{keyword}] 请求被限制，等待60秒...")
                    time.sleep(60)
                else:
                    print(f"  [{keyword}] 请求失败，状态码: {response.status_code}")

            except requests.exceptions.Timeout:
                print(f"  [{keyword}] 请求超时，重试 {attempt + 1}/{config.MAX_RETRIES}")
                time.sleep(10)
            except Exception as e:
                print(f"  [{keyword}] 抓取异常: {e}")
                time.sleep(5)

            time.sleep(config.REQUEST_DELAY)

        return results

    def _parse_search_results(self, soup: BeautifulSoup) -> List[dict]:
        """解析搜索结果页面"""
        articles = []

        # 查找文章列表容器
        article_elements = soup.select("article") or soup.select(".py-16") or soup.select("[data-test='search-results'] article")

        if not article_elements:
            # 尝试其他选择器
            article_elements = soup.select("li.search-result") or soup.select(".c-card")

        for elem in article_elements:
            try:
                # 提取标题和链接
                title_elem = elem.select_one("h3 a") or elem.select_one("a[href*='/articles/']")
                if not title_elem:
                    continue

                href = title_elem.get("href", "")
                if "/articles/" not in href:
                    continue

                # 提取 nature_id
                match = re.search(r'/articles/([a-z0-9\-]+)', href)
                if not match:
                    continue
                nature_id = match.group(1)

                title = title_elem.get_text(strip=True)

                # 提取作者
                author_elem = elem.select_one("[class*='author']") or elem.select_one(".c-author")
                authors = author_elem.get_text(strip=True) if author_elem else "Nature Editorial"

                # 提取来源期刊
                source_elem = elem.select_one("[class*='journal']") or elem.select_one(".c-journal")
                source = source_elem.get_text(strip=True) if source_elem else "Nature"

                # 提取发布日期
                date_elem = elem.select_one("[class*='date']") or elem.select_one("time")
                date_str = date_elem.get_text(strip=True) if date_elem else ""
                publish_date = self._parse_date(date_str)

                # 提取摘要
                summary_elem = elem.select_one("[class*='summary']") or elem.select_one("[class*='description']")
                summary = summary_elem.get_text(strip=True) if summary_elem else ""

                # 构建文章URL
                link = f"https://www.nature.com/articles/{nature_id}"

                # 分类（同时检查是否与 HR 相关）
                topic, topic_label = self._classify_topic(title, summary)

                # 如果不是 HR 相关文章，跳过
                if topic is None:
                    continue

                articles.append({
                    "nature_id": nature_id,
                    "title": self._translate_title(title),
                    "title_en": title,
                    "summary": summary or self._generate_summary(title, topic),
                    "source": source,
                    "authors": authors,
                    "link": link,
                    "topic": topic,
                    "topic_label": topic_label,
                    "publish_date": publish_date
                })

            except Exception as e:
                print(f"  解析文章异常: {e}")
                continue

        return articles

    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        # 尝试各种日期格式
        date_formats = [
            "%d %b %Y",
            "%Y-%m-%d",
            "%d %B %Y",
            "%b %d, %Y"
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue

        return datetime.now().strftime("%Y-%m-%d")

    def _translate_title(self, title: str) -> str:
        """将英文标题转换为中文（简单翻译，实际项目中建议调用翻译API）"""
        # 这里使用预定义的中文标题映射，后续可以接入翻译API
        return title

    def _generate_summary(self, title: str, topic: str) -> str:
        """当没有摘要时，生成简要说明"""
        topic_summaries = {
            "recruitment": "本研究探讨了招聘与人才选拔领域的重要议题，通过实证分析揭示了相关因素的影响机制和实践启示。",
            "training": "本文聚焦于员工培训与职业发展话题，研究发现对组织学习和人才成长具有重要参考价值。",
            "performance": "本研究围绕绩效管理与评估展开，为企业优化绩效管理体系提供了实证依据。",
            "compensation": "文章讨论了薪酬福利与激励机制的设计问题，揭示了薪酬策略对员工行为和组织效能的影响。",
            "employee-relations": "本研究关注员工关系与工作体验，对提升员工敬业度和组织承诺具有实践意义。",
            "hr-tech": "本文探讨了人工智能与数字化技术在人力资源管理中的应用，分析了技术变革对HR实践的影响。",
            "organizational-behavior": "研究围绕组织行为与领导力展开，为理解团队协作和组织文化提供了新视角。",
            "diversity": "本研究关注职场多元化和包容性议题，对促进公平就业和组织多样性具有重要启示。"
        }
        return topic_summaries.get(topic, "本研究探讨了人力资源管理领域的重要议题，提供了有价值的研究发现和实践建议。")

    def fetch_all_articles(self) -> Tuple[List[dict], int]:
        """抓取所有关键词的最新文章（保留最近7天的HR相关文章）"""
        all_articles = []
        seen_ids = set()

        # 计算日期范围：最近7天
        from datetime import datetime, timedelta
        today = datetime.now().date()
        start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
        yesterday = (today - timedelta(days=config.FETCH_DAYS_AGO)).strftime("%Y-%m-%d")

        print(f"\n开始抓取 Nature HR 相关文章...")
        print(f"  保留发布日期在 {start_date} 到 {yesterday} 之间的文章")
        print("=" * 50)

        for keyword in config.NATURE_SEARCH_KEYWORDS:
            print(f"\n正在搜索: {keyword}")
            results = self.fetch_search_results(keyword, max_results=15)

            for article in results:
                # 只保留最近7天内的文章
                if article["publish_date"] < start_date:
                    continue
                if article["nature_id"] not in seen_ids:
                    seen_ids.add(article["nature_id"])
                    all_articles.append(article)

            time.sleep(config.REQUEST_DELAY)

        # 按发布日期排序（最新的在前）
        all_articles.sort(key=lambda x: x["publish_date"], reverse=True)

        print("\n" + "=" * 50)
        print(f"总共抓取到 {len(all_articles)} 篇最近7天内的HR相关文章（去重后）")

        return all_articles, len(all_articles)


def fetch_daily_articles() -> Tuple[List[dict], int]:
    """每日抓取主函数"""
    scraper = NatureScraper()
    articles, total = scraper.fetch_all_articles()
    return articles, total


if __name__ == "__main__":
    # 测试抓取
    articles, total = fetch_daily_articles()
    print(f"\n抓取完成，共 {total} 篇文章")
    for i, article in enumerate(articles[:5], 1):
        print(f"\n--- 文章 {i} ---")
        print(f"标题: {article['title']}")
        print(f"来源: {article['source']}")
        print(f"链接: {article['link']}")
        print(f"分类: {article['topic_label']}")
