#!/usr/bin/env python3
"""
构建纯静态页面 - 将 data.js、app.js、styles.css 内联到 index.html 中
并注入 API 拦截代码，使页面在纯静态环境（EdgeOne Pages）下也能正常运行

原理：解析 data.js 中的 dailyResearchData，预生成所有 API 接口的返回数据，
通过覆盖 window.fetch 拦截前端的所有 API 请求，直接返回预生成的静态数据。
这样页面不依赖任何后端服务，部署到 EdgeOne Pages 后即可独立运行。
"""
import os
import re
import json


def extract_daily_research_data(data_js_content):
    """从 data.js 中提取 dailyResearchData 的 JSON 数据"""
    match = re.search(r'const\s+dailyResearchData\s*=\s*(\[.*?\]);', data_js_content, re.DOTALL)
    if not match:
        raise ValueError("无法在 data.js 中找到 dailyResearchData")
    return json.loads(match.group(1))


def generate_static_api_stub(data):
    """基于 dailyResearchData 生成 API 拦截器的 JavaScript 代码"""
    # 扁平化所有文章，并补充日期字段（让 app.js 的分组/筛选逻辑正常工作）
    all_articles = []
    for day in data:
        day_date = day['date']
        for article in day.get('articles', []):
            article_copy = dict(article)
            article_copy['push_date'] = article_copy.get('push_date') or day_date
            article_copy['publish_date'] = article_copy.get('publish_date') or day_date
            article_copy['fetched_date'] = article_copy.get('fetched_date') or day_date
            article_copy['created_at'] = article_copy.get('created_at') or day_date
            all_articles.append(article_copy)

    # 提取 Sources（去重）
    source_set = set()
    for a in all_articles:
        source_set.add(a.get('source', '未知来源'))
    sources = [{'value': s, 'label': s} for s in sorted(source_set)]

    # 提取 Topics（去重）
    topic_set = set()
    topic_labels = {}
    for a in all_articles:
        topic = a.get('topic', '')
        if topic:
            topic_set.add(topic)
            topic_labels[topic] = a.get('topicLabel', topic)
    topics = [{'value': t, 'label': topic_labels.get(t, t)} for t in sorted(topic_set)]

    # Stats 统计数据
    stats = {
        'total_articles': len(all_articles),
        'total_subscribers': 0
    }

    # Calendar 推送日历
    calendar = [
        {
            'date': day['date'],
            'weekday': day.get('weekday', ''),
            'article_count': len(day.get('articles', []))
        }
        for day in data
    ]

    latest_date = data[0]['date'] if data else '--'

    # JSON 序列化（确保在 JS 字符串中安全）
    sources_json = json.dumps(sources, ensure_ascii=False)
    topics_json = json.dumps(topics, ensure_ascii=False)
    stats_json = json.dumps(stats, ensure_ascii=False)
    calendar_json = json.dumps(calendar, ensure_ascii=False)
    all_articles_json = json.dumps(all_articles, ensure_ascii=False)
    latest_date_json = json.dumps(latest_date, ensure_ascii=False)

    stub = f'''
// ===== 静态模式 API 拦截器（由 build_static.py 自动生成）=====
(function() {{
    const STATIC_SOURCES = {sources_json};
    const STATIC_TOPICS = {topics_json};
    const STATIC_STATS = {stats_json};
    const STATIC_CALENDAR = {calendar_json};
    const STATIC_ARTICLES = {all_articles_json};
    const LATEST_DATE = {latest_date_json};

    function buildResponse(data) {{
        return new Response(JSON.stringify({{code: 200, data: data}}), {{
            status: 200,
            headers: {{'Content-Type': 'application/json'}}
        }});
    }}

    const originalFetch = window.fetch;
    window.fetch = async function(url, options) {{
        const urlStr = (typeof url === 'string') ? url : (url.href || url.toString());

        // 拦截 /api/sources
        if (urlStr.includes('/api/sources')) {{
            return buildResponse(STATIC_SOURCES);
        }}

        // 拦截 /api/topics
        if (urlStr.includes('/api/topics')) {{
            return buildResponse(STATIC_TOPICS);
        }}

        // 拦截 /api/stats
        if (urlStr.includes('/api/stats')) {{
            return buildResponse(STATIC_STATS);
        }}

        // 拦截 /api/admin/status
        if (urlStr.includes('/api/admin/status')) {{
            return buildResponse({{
                last_push: LATEST_DATE,
                next_push: '--',
                scheduler_running: false
            }});
        }}

        // 拦截 /api/push-calendar
        if (urlStr.includes('/api/push-calendar')) {{
            return buildResponse(STATIC_CALENDAR);
        }}

        // 拦截 /api/articles（支持筛选和分页）
        if (urlStr.includes('/api/articles')) {{
            const urlObj = new URL(urlStr, window.location.href);
            const dateFilter = urlObj.searchParams.get('date');
            const topicFilter = urlObj.searchParams.get('topic');
            const sourceFilter = urlObj.searchParams.get('source');
            const searchFilter = urlObj.searchParams.get('search');

            let filtered = STATIC_ARTICLES.slice();

            if (dateFilter && dateFilter !== 'all') {{
                filtered = filtered.filter(a =>
                    (a.push_date || a.publish_date || a.fetched_date || '').startsWith(dateFilter)
                );
            }}
            if (topicFilter && topicFilter !== 'all') {{
                filtered = filtered.filter(a => a.topic === topicFilter);
            }}
            if (sourceFilter && sourceFilter !== 'all') {{
                filtered = filtered.filter(a => a.source === sourceFilter);
            }}
            if (searchFilter) {{
                const s = searchFilter.toLowerCase();
                filtered = filtered.filter(a =>
                    (a.title || '').toLowerCase().includes(s) ||
                    (a.summary || '').toLowerCase().includes(s)
                );
            }}

            const page = parseInt(urlObj.searchParams.get('page') || '1', 10);
            const pageSize = parseInt(urlObj.searchParams.get('page_size') || '10', 10);
            const start = (page - 1) * pageSize;
            const paginated = filtered.slice(start, start + pageSize);

            return buildResponse({{
                total: filtered.length,
                page: page,
                page_size: pageSize,
                articles: paginated
            }});
        }}

        // 其他请求走原生的 fetch
        return originalFetch(url, options);
    }};

    console.log('[静态模式] API 拦截器已启用，所有数据来源于内联的 dailyResearchData');
}})();
// ===== 拦截器结束 =====
'''
    return stub


def build_static():
    # 读取源文件
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    with open('app.js', 'r', encoding='utf-8') as f:
        app_js = f.read()

    with open('data.js', 'r', encoding='utf-8') as f:
        data_js = f.read()

    with open('styles.css', 'r', encoding='utf-8') as f:
        styles_css = f.read()

    # 解析 dailyResearchData 并生成 API 拦截器
    try:
        research_data = extract_daily_research_data(data_js)
        api_stub = generate_static_api_stub(research_data)
        print(f'✅ 已从 data.js 解析 {len(research_data)} 天的数据，共生成预计算 API 数据')
    except Exception as e:
        print(f'⚠️ 生成 API 拦截器失败: {e}')
        api_stub = ''

    # 创建 static 目录
    os.makedirs('static', exist_ok=True)

    # 1. 内联 styles.css
    html = html.replace(
        '<link rel="stylesheet" href="styles.css">',
        f'<style>\n{styles_css}\n</style>'
    )

    # 2. 内联 data.js，并在其后插入 API 拦截器（这样 app.js 里的 fetch 会被拦截）
    html = html.replace(
        '<script src="data.js"></script>',
        f'<script>\n{data_js}\n{api_stub}\n</script>'
    )

    # 3. 内联 app.js
    html = html.replace(
        '<script src="app.js"></script>',
        f'<script>\n{app_js}\n</script>'
    )

    # 写入 static/index.html（备用）
    with open('static/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    # 同时更新根目录的 index.html（用于 EdgeOne Pages 部署）
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print('✅ 纯静态页面构建完成')
    print(f'   static/index.html: {os.path.getsize("static/index.html")} bytes')
    print(f'   index.html: {os.path.getsize("index.html")} bytes')
    print('   该页面已完全不依赖后端 API，可直接部署到 EdgeOne Pages')


if __name__ == "__main__":
    build_static()
