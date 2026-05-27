#!/bin/bash
# HR信息日报 - 一键部署脚本
# 用于手动触发部署到 GitHub

set -e

echo "🚀 开始部署 HR信息日报..."

# 1. 构建静态文件
echo "📦 构建静态页面..."
cat > build.py << 'EOF'
import os
import json
from datetime import datetime

# 读取前端文件
index_html = open('index.html', 'r', encoding='utf-8').read()
app_js = open('app.js', 'r', encoding='utf-8').read()
data_js = open('data.js', 'r', encoding='utf-8').read()
styles_css = open('styles.css', 'r', encoding='utf-8').read()

# 创建静态页面
static_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HR信息日报 - 人力资源管理信息追踪</title>
    <link rel="stylesheet" href="data:text/css,{styles_css.replace(chr(10), chr(10)+"    ")}" />
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
os.makedirs('static', exist_ok=True)
open('static/index.html', 'w', encoding='utf-8').write(static_html)
print('✅ 静态页面构建完成')
EOF
python3 build.py
rm build.py

# 2. 添加所有更改
echo "📝 准备提交..."
git add .

# 3. 检查是否有更改
if git diff --cached --quiet; then
    echo "✅ 没有需要提交的更改"
    exit 0
fi

# 4. 提交
echo "💾 提交更改..."
git commit -m "自动更新日报数据 - $(date '+%Y-%m-%d %H:%M')"

# 5. 推送到 GitHub
echo "📤 推送到 GitHub..."
git push

echo "🎉 部署完成！"
echo "   - 代码已推送到 GitHub"
echo "   - EdgeOne Pages 将自动更新"
echo "   - 本地服务继续运行（邮件推送）"
