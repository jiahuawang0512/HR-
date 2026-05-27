#!/usr/bin/env python3
"""
构建静态页面 - 将 data.js 和 app.js 内联到 index.html 中
"""
import os

def build_static():
    # 读取文件
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    with open('app.js', 'r', encoding='utf-8') as f:
        app_js = f.read()
    
    with open('data.js', 'r', encoding='utf-8') as f:
        data_js = f.read()
    
    with open('styles.css', 'r', encoding='utf-8') as f:
        styles_css = f.read()
    
    # 创建 static 目录
    os.makedirs('static', exist_ok=True)
    
    # 替换外部引用为内联内容
    # 1. 替换 styles.css 引用
    html = html.replace(
        '<link rel="stylesheet" href="styles.css">',
        f'<style>\n{styles_css}\n</style>'
    )
    
    # 2. 替换 data.js 引用
    html = html.replace(
        '<script src="data.js"></script>',
        f'<script>\n{data_js}\n</script>'
    )
    
    # 3. 替换 app.js 引用
    html = html.replace(
        '<script src="app.js"></script>',
        f'<script>\n{app_js}\n</script>'
    )
    
    # 写入 static/index.html
    with open('static/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # 同时更新根目录的 index.html（用于 EdgeOne Pages 部署）
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print('✅ 静态页面构建完成')
    print(f'   static/index.html: {os.path.getsize("static/index.html")} bytes')
    print(f'   index.html: {os.path.getsize("index.html")} bytes')

if __name__ == "__main__":
    build_static()
