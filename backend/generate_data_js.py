#!/usr/bin/env python3
"""
HR信息日报 - 生成 data.js 脚本
从 SQLite 数据库读取文章数据，生成前端使用的 data.js 文件
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_articles, init_database


def generate_data_js(output_path: str = None) -> dict:
    """从数据库生成 data.js 文件"""
    
    # 默认输出到项目根目录的 data.js
    if output_path is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(project_root, "data.js")
    """从数据库生成 data.js 文件"""
    
    # 初始化数据库
    init_database()
    
    # 获取所有文章
    articles, total = get_articles(page=1, page_size=1000)
    print(f"数据库中共有 {total} 篇文章")
    
    # 按日期分组
    groups = {}
    for article in articles:
        date = article.push_date or article.publish_date or article.fetched_date[:10]
        if date not in groups:
            groups[date] = []
        groups[date].append({
            "id": article.id,
            "title": article.title,
            "topic": article.topic,
            "topicLabel": article.topic_label,
            "summary": article.summary,
            "source": article.source_short or article.source,
            "authors": article.authors,
            "link": article.link
        })
    
    # 构建 data.js 内容
    weekdays = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    data_items = []
    
    for date in sorted(groups.keys(), reverse=True):
        dt = datetime.strptime(date, "%Y-%m-%d")
        weekday = weekdays[dt.weekday()]
        data_items.append({
            "date": date,
            "weekday": weekday,
            "articles": groups[date]
        })
    
    # 写入 data.js
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_js_content = "// ========== HR信息日报 - 自动更新数据 ==========\n"
    data_js_content += f"// 最后更新: {now_str}\n"
    data_js_content += f"// 文章总数: {total}\n\n"
    data_js_content += "const dailyResearchData = " + json.dumps(data_items, ensure_ascii=False, indent=4) + ";\n"
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(data_js_content)
    
    result = {
        "total_articles": total,
        "days": len(data_items),
        "output_path": os.path.abspath(output_path)
    }
    print(f"✅ data.js 已更新: {result['output_path']}")
    print(f"   共 {result['days']} 天 {result['total_articles']} 篇文章")
    
    return result


if __name__ == "__main__":
    generate_data_js()
