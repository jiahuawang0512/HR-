# HR信息日报 - 自动部署指南

## 功能说明

本系统实现了全自动部署：
- ✅ GitHub Actions 每天自动抓取文章
- ✅ 自动构建静态页面
- ✅ 自动推送到 GitHub
- ✅ EdgeOne Pages 自动更新公网页面
- ✅ 本地服务继续运行（邮件推送）

## 工作流程

```
每天 08:30 (北京时间)
       │
       ▼
┌─────────────────┐
│  GitHub Actions │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  抓取 Nature/HBR │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  构建静态页面    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐  ┌─────────┐
│GitHub │  │EdgeOne  │
│ Push  │  │ Pages   │
└───────┘  └─────────┘
    │
    ▼
┌─────────────────┐
│  公网页面更新    │
└─────────────────┘
```

## 配置步骤

### 1. 配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

| Secret 名称 | 说明 |
|------------|------|
| `GITHUB_TOKEN` | GitHub Personal Access Token |
| `EDGEONE_TOKEN` | EdgeOne Pages API Token |
| `EDGEONE_PROJECT` | EdgeOne Pages 项目 ID |

#### 获取 EdgeOne Token
1. 登录 EdgeOne Pages 控制台
2. 进入「设置」→「访问令牌」
3. 创建新令牌，勾选 `pages:write` 权限
4. 复制 Token

### 2. 推送到 GitHub

```bash
git add .
git commit -m "添加自动部署配置"
git push
```

推送后，GitHub Actions 会自动触发一次运行。

## 本地服务（邮件推送）

GitHub Actions 无法直接发送邮件，邮件推送功能需要本地服务运行。

### 启动本地服务

```bash
# 使用 launchd 开机自启（已配置）
launchctl load ~/Library/LaunchAgents/com.hr.daily.report.plist

# 或手动启动
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 本地服务职责

| 功能 | 运行位置 |
|-----|---------|
| 邮件推送 | 本地服务 |
| 定时抓取 | GitHub Actions + 本地服务 |
| 公网页面 | EdgeOne Pages |
| 订阅管理 | 本地服务 |

## 手动部署

如果需要立即更新公网页面：

```bash
./deploy.sh
```

或手动执行：

```bash
git add .
git commit -m "更新日报"
git push
```

## 查看部署状态

### GitHub Actions 状态
访问：`https://github.com/你的用户名/hr-daily/actions`

### EdgeOne Pages 状态
访问你的 EdgeOne Pages 项目控制台。

## 常见问题

### Q: 公网页面没有更新？

1. 检查 GitHub Actions 是否运行成功
2. 检查 EdgeOne Token 是否有效
3. 手动运行 `./deploy.sh` 测试

### Q: 邮件没有收到？

邮件推送需要本地服务运行。确保：
1. 本地服务已启动
2. SMTP 配置正确
3. 订阅者邮箱有效

### Q: 如何修改定时时间？

编辑 `.github/workflows/daily-update.yml`：

```yaml
schedule:
  - cron: "30 0 * * *"  # UTC 时间，修改这里
```

## 目录结构

```
hr-daily/
├── .github/
│   └── workflows/
│       └── daily-update.yml  # GitHub Actions 配置
├── backend/
│   ├── main.py               # FastAPI 主入口
│   ├── scraper.py            # Nature 抓取
│   ├── scraper_hbr_cn.py     # HBR 中文版抓取
│   ├── pusher.py             # 邮件推送
│   ├── scheduler.py          # 定时任务
│   └── ...
├── index.html                # 前端页面
├── app.js                    # 前端逻辑
├── data.js                   # 数据
├── styles.css                # 样式
├── deploy.sh                 # 一键部署脚本
└── hr_daily.db               # 本地数据库
```
