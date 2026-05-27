#!/usr/bin/env python3
import os

# 读取前端文件
index_html = open('index.html', 'r', encoding='utf-8').read()
app_js = open('app.js', 'r', encoding='utf-8').read()
data_js = open('data.js', 'r', encoding='utf-8').read()
styles_css = open('styles.css', 'r', encoding='utf-8').read()

# 创建静态目录
os.makedirs('static', exist_ok=True)

# 创建静态页面
static_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HR信息日报 - 人力资源管理信息追踪</title>
    <link rel="stylesheet" href="data:text/css,{styles_css.replace(chr(10), chr(10)+'    ')}" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    {index_html.replace('<script src="data.js"></script>', '').replace('<script src="app.js"></script>', '')}
    <script>
        {data_js}
        {app_js}
    </script>
</body>
</html>'''

# 写入静态文件
open('static/index.html', 'w', encoding='utf-8').write(static_html)
print('✅ 静态页面构建完成')
