# GitHub Actions 配置指南

## 手动配置步骤

由于当前 GitHub Token 缺少 `workflow` 权限，需要你在 GitHub 网站上手动创建工作流文件。

### 步骤 1: 进入 GitHub 仓库
打开 https://github.com/jiahuawang0512/HR-

### 步骤 2: 创建工作流文件
1. 点击 **Actions** 标签
2. 点击 **New workflow** 或 **set up a workflow yourself**
3. 将以下文件内容复制进去：

**文件路径**: `.github/workflows/daily-fetch.yml`

```yaml
name: Daily Fetch and Deploy

on:
  schedule:
    # 每天北京时间 10:30 运行（UTC 02:30）
    - cron: '30 2 * * *'
  workflow_dispatch:
    inputs:
      reason:
        description: '手动触发原因'
        required: false
        default: '手动触发抓取'

permissions:
  contents: write

jobs:
  fetch-and-update:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        
    - name: Run fetch script and update data.js
      run: |
        cd backend
        python -c "
from scheduler import job_fetch_articles
from generate_data_js import generate_data_js

# 执行抓取
result = job_fetch_articles()
print(f'抓取结果: {result}')

# 生成 data.js
generate_data_js()
"
        
    - name: Commit and push changes
      run: |
        git config user.name "github-actions[bot]"
        git config user.email "github-actions[bot]@users.noreply.github.com"
        git add data.js
        git diff --cached --quiet || (git commit -m "🤖 自动更新: $(date +%Y-%m-%d) 抓取结果" && git push)
        
    - name: Deployment Summary
      run: |
        echo "✅ 抓取和部署完成"
        echo "时间: $(date)"
```

4. 点击 **Commit changes...**

### 步骤 3: 验证工作流
1. 进入 **Actions** 页面
2. 应该能看到 **Daily Fetch and Deploy** 工作流
3. 点击 **Run workflow** 可以手动测试

---

## 自动化流程说明

配置完成后，整个自动化链路如下：

```
每天 10:30 (北京时间)
    ↓
GitHub Actions 自动触发
    ↓
1. 安装 Python 依赖
2. 运行抓取脚本 (Nature + HBR)
3. 生成新的 data.js
4. 自动提交到 GitHub
    ↓
EdgeOne Pages 检测到代码更新
    ↓
自动重新构建并部署到公网
    ↓
公网页面展示最新内容
```

## 手动触发

除了每日自动运行，你也可以随时手动触发：
1. 进入 GitHub 仓库 → Actions
2. 选择 **Daily Fetch and Deploy**
3. 点击右侧 **Run workflow**

## 注意事项

- 抓取任务需要网络访问，GitHub Actions  runner 可以正常访问外网
- 如果某天没有新文章，data.js 仍会更新（保持原有数据）
- 邮件推送功能需要配置 SMTP（在仓库 Secrets 中设置）
