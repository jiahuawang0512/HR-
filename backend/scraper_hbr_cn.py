import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import config


class HBRCaiJingScraper:
    """哈佛商业评论中文版 (hbrchina.org) 抓取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.hbrchina.org/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
        # 禁用SSL证书验证（hbrchina.org证书已过期）
        self.session.verify = False
        self.base_url = "https://www.hbrchina.org"

    def fetch_articles(self) -> list:
        """抓取首页文章，保留最近7天内的HR相关文章"""
        articles = []
        seen_ids = set()

        try:
            # 计算日期范围：最近7天
            today = datetime.now().date()
            start_date = (today - timedelta(days=7)).strftime("%Y-%m-%d")
            yesterday = (today - timedelta(days=config.FETCH_DAYS_AGO)).strftime("%Y-%m-%d")
            
            print(f"  [HBR中文] 保留发布日期在 {start_date} 之后的文章")

            # 抓取首页文章列表
            response = self.session.get(self.base_url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "lxml")

                # 查找文章列表
                article_elements = soup.select("article") or soup.select(".article-item") or soup.select("li.article")

                for elem in article_elements:
                    try:
                        # 提取标题和链接
                        title_elem = elem.select_one("h3 a") or elem.select_one("a[href*='/article/']") or elem.select_one("a[href*='/topic/']")
                        if not title_elem:
                            continue

                        title = title_elem.get_text(strip=True)
                        href = title_elem.get("href", "")

                        if not href or "/article/" not in href:
                            continue

                        # 提取文章ID
                        import re
                        match = re.search(r'/article/(\d+)', href)
                        if not match:
                            continue
                        article_id = match.group(1)

                        # 构建完整链接
                        link = f"{self.base_url}/article/{article_id}"

                        # 提取发布日期
                        date_elem = elem.select_one(".date") or elem.select_one("time") or elem.select_one("[class*='date']")
                        date_str = date_elem.get_text(strip=True) if date_elem else ""
                        publish_date = self._parse_date(date_str)

                        # 只保留最近7天内的文章
                        if publish_date < start_date:
                            continue

                        # 提取摘要
                        summary_elem = elem.select_one(".summary") or elem.select_one(".description") or elem.select_one("p")
                        summary = summary_elem.get_text(strip=True) if summary_elem else ""

                        # HR 相关性校验
                        text = (title + " " + summary).lower()
                        is_hr_related = any(kw in text for kw in config.HBR_CN_HR_KEYWORDS)
                        if not is_hr_related:
                            continue

                        if article_id and article_id not in seen_ids:
                            seen_ids.add(article_id)
                            articles.append({
                                "hbr_id": article_id,
                                "nature_id": article_id,
                                "title": title,
                                "link": link,
                                "source": "哈佛商业评论中文版",
                                "source_short": "HBR中文",
                                "authors": "HBR China",
                                "publish_date": publish_date,
                                "topic": self._classify_topic(text),
                                "topic_label": self._get_topic_label(text),
                                "summary": summary[:200] if summary else ""
                            })
                    except Exception as e:
                        print(f"  解析HBR文章异常: {e}")
                        continue

            # 按发布日期排序（最新的在前）
            articles.sort(key=lambda x: x["publish_date"], reverse=True)
            
            print(f"  [HBR中文] 成功抓取到 {len(articles)} 条最近7天内的HR相关文章")
        except Exception as e:
            print(f"抓取HBR中文网站异常: {e}")

        return articles

    def _parse_date(self, date_str: str) -> str:
        """解析日期字符串"""
        if not date_str:
            return datetime.now().strftime("%Y-%m-%d")

        # 尝试解析中文日期格式，如 "2025年09月11日" 或 "2025-09-11"
        try:
            date_str = date_str.replace(" ", "").replace("　", "")
            if "年" in date_str and "月" in date_str:
                year = int(date_str.split("年")[0])
                month = int(date_str.split("年")[1].split("月")[0])
                day = int(date_str.split("月")[1].split("日")[0])
                return f"{year}-{month:02d}-{day:02d}"
            elif "-" in date_str and len(date_str) == 10:
                return date_str[:10]
        except Exception:
            pass

        return datetime.now().strftime("%Y-%m-%d")

    def _classify_topic(self, text: str) -> str:
        """根据关键词分类文章"""
        topic_mapping = {
            "recruitment": ["招聘", "选拔", "面试", "录用", "人才获取"],
            "training": ["培训", "发展", "学习", "导师制", "教练"],
            "performance": ["绩效", "KPI", "OKR", "考核", "评估"],
            "compensation": ["薪酬", "薪资", "福利", "激励", "奖金"],
            "employee-relations": ["员工", "职场", "敬业度", "满意度", "留存", "离职"],
            "hr-tech": ["HR科技", "人工智能", "AI", "数字化", "自动化"],
            "organizational-behavior": ["组织", "领导力", "文化", "团队", "协作"],
            "diversity": ["多元化", "包容性", "公平", "偏见", "歧视"]
        }

        best_topic = "organizational-behavior"
        best_score = 0

        for topic, keywords in topic_mapping.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > best_score:
                best_score = score
                best_topic = topic

        return best_topic

    def _get_topic_label(self, text: str) -> str:
        """获取分类标签"""
        topic_labels = {
            "recruitment": "招聘与选拔",
            "training": "培训与发展",
            "performance": "绩效管理",
            "compensation": "薪酬福利",
            "employee-relations": "员工关系",
            "hr-tech": "HR科技与AI",
            "organizational-behavior": "组织行为学",
            "diversity": "多元化与包容性"
        }
        topic = self._classify_topic(text)
        return topic_labels.get(topic, "组织行为学")


if __name__ == "__main__":
    scraper = HBRCaiJingScraper()
    articles = scraper.fetch_articles()
    for a in articles:
        print(a)
