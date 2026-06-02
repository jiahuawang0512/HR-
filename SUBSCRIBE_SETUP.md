# 订阅推送 - 部署说明

页面"订阅推送"按钮 → EdgeOne Pages Function `/api/subscribe` → 把邮箱写入仓库 `subscribers.json` → GitHub Actions 每天读取并发送邮件。

无需任何后端服务器。

---

## 一、整体流程

```
访客点订阅                                        每天 10:15 / 18:30 (北京时间)
    │                                                    │
    ▼                                                    ▼
EdgeOne Pages Function (/api/subscribe)          GitHub Actions
    │                                                    │
    │ 用 GitHub Token PUT subscribers.json               │ 抓取新文章
    ▼                                                    │ 读 subscribers.json
GitHub 仓库 (subscribers.json)  ◀──────────────────── 发送邮件
```

---

## 二、需要配置的密钥（共 3 处）

### 1. GitHub 仓库 Secrets （Settings → Secrets and variables → Actions）

| Name | Value | 用途 |
| --- | --- | --- |
| `SMTP_USER` | 您的发件 QQ 邮箱（如 `xxx@qq.com`） | 邮件发件账号 |
| `SMTP_PASSWORD` | QQ 邮箱**授权码**（不是登录密码） | 邮件发件密码 |

> SMTP_HOST / SMTP_PORT / USE_SSL 已默认 `smtp.qq.com:465 SSL`，无需配置。
> 不需要配 `MAIL_TO`，脚本会自动读 `subscribers.json`。

### 2. 创建 GitHub PAT（仅用于 EdgeOne Function 写入 subscribers.json）

1. 打开 https://github.com/settings/tokens?type=beta
2. **Generate new token (Fine-grained personal access token)**
3. 配置：
   - **Token name**: `edgeone-subscribe-fn`
   - **Expiration**: 90 天 / 1 年（到期前续期即可）
   - **Repository access**: Only select repositories → 选择 `jiahuawang0512/HR-`
   - **Repository permissions** → **Contents**: **Read and write**
4. **Generate token**，复制以 `github_pat_` 开头的字符串

### 3. EdgeOne Pages 项目环境变量（控制台 → 项目 → 环境变量）

| Name | Value | 备注 |
| --- | --- | --- |
| `GITHUB_TOKEN` | 上一步生成的 PAT | 让 Function 能写入仓库 |
| `GITHUB_REPO` | `jiahuawang0512/HR-` | 仓库 owner/name |
| `GITHUB_BRANCH` | `main` | 默认分支 |

> 配完后必须重新部署一次（推一个 commit 即可触发）才会注入到 Function 运行时。

---

## 三、Functions 路径与文件清单

| URL | 文件 | 作用 |
| --- | --- | --- |
| `POST /api/subscribe` | `functions/api/subscribe.js` | 新增/更新订阅 |
| `POST /api/unsubscribe` | `functions/api/unsubscribe.js` | 取消订阅 |
| `GET /api/subscribers/count` | `functions/api/subscribers/count.js` | 订阅人数 |
| `GET /api/admin/status` | `functions/api/admin/status.js` | 系统状态（stub，永远 running） |
| `GET /api/stats` | `functions/api/stats.js` | 综合统计（含订阅人数） |

存储文件：`subscribers.json`（仓库根目录，Function 通过 GitHub Contents API 读写）。

---

## 四、本地验证（可选）

```bash
# 1) 看 send_email.py 能不能正确读 subscribers.json
python3 -c "
import sys; sys.path += ['backend', '.github/scripts']
import send_email
print(send_email.get_recipients_from_json())
"

# 2) 在 EdgeOne 部署后，curl 验证 Function
curl -X POST https://<your-edgeone-domain>/api/subscribe \
     -H 'content-type: application/json' \
     -d '{"email":"test@example.com","interests":["recruitment"]}'
# 预期返回：{"code":200,"message":"订阅成功","data":{"count":4}}

curl https://<your-edgeone-domain>/api/subscribers/count
# 预期返回：{"code":200,"data":{"count":4}}
```

如果 `/api/subscribe` 返回 `服务端未配置 GITHUB_TOKEN/GITHUB_REPO`，说明 EdgeOne 环境变量没配；如果返回 `GitHub PUT ... 401/403`，说明 PAT 权限不足或过期。

---

## 五、未来运维

- 想看现有订阅者：直接看 GitHub 仓库的 `subscribers.json`
- 想手动加/删订阅者：直接编辑 `subscribers.json` 提交即可
- PAT 过期：在 EdgeOne 控制台覆盖 `GITHUB_TOKEN` 即可，无需改代码
- 想换其它邮箱：在 GitHub Secrets 里加 `SMTP_HOST / SMTP_PORT / USE_SSL` 覆盖默认 QQ 配置即可
