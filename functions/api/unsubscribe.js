// EdgeOne Pages Function: 取消订阅
// 路径：POST /api/unsubscribe?email=xxx 或 body { email }

const GITHUB_API = "https://api.github.com";

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": "*",
      "access-control-allow-headers": "content-type",
      "access-control-allow-methods": "POST, OPTIONS",
    },
  });
}
function b64encode(str) {
  if (typeof btoa === "function") return btoa(unescape(encodeURIComponent(str)));
  return Buffer.from(str, "utf-8").toString("base64");
}
function b64decode(str) {
  if (typeof atob === "function") return decodeURIComponent(escape(atob(str.replace(/\s/g, ""))));
  return Buffer.from(str, "base64").toString("utf-8");
}
async function ghReadFile(env, path) {
  const url = `${GITHUB_API}/repos/${env.GITHUB_REPO}/contents/${path}?ref=${env.GITHUB_BRANCH || "main"}`;
  const r = await fetch(url, {
    headers: {
      authorization: `Bearer ${env.GITHUB_TOKEN}`,
      "user-agent": "edgeone-pages-fn",
      accept: "application/vnd.github+json",
    },
  });
  if (!r.ok) throw new Error(`GitHub GET ${r.status}: ${await r.text()}`);
  const data = await r.json();
  return { content: JSON.parse(b64decode(data.content)), sha: data.sha };
}
async function ghWriteFile(env, path, content, sha, message) {
  const url = `${GITHUB_API}/repos/${env.GITHUB_REPO}/contents/${path}`;
  const r = await fetch(url, {
    method: "PUT",
    headers: {
      authorization: `Bearer ${env.GITHUB_TOKEN}`,
      "user-agent": "edgeone-pages-fn",
      accept: "application/vnd.github+json",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      message,
      content: b64encode(JSON.stringify(content, null, 2) + "\n"),
      sha,
      branch: env.GITHUB_BRANCH || "main",
    }),
  });
  if (!r.ok) throw new Error(`GitHub PUT ${r.status}: ${await r.text()}`);
  return r.json();
}

export async function onRequestOptions() {
  return json({}, 204);
}

export async function onRequestPost(context) {
  const { request, env } = context;
  if (!env.GITHUB_TOKEN || !env.GITHUB_REPO) {
    return json({ code: 500, message: "服务端未配置" }, 500);
  }
  const url = new URL(request.url);
  let email = (url.searchParams.get("email") || "").trim().toLowerCase();
  if (!email) {
    try {
      const body = await request.json();
      email = (body.email || "").trim().toLowerCase();
    } catch (_) {}
  }
  if (!email) return json({ code: 400, message: "缺少 email 参数" }, 400);

  try {
    const { content, sha } = await ghReadFile(env, "subscribers.json");
    const list = Array.isArray(content.subscribers) ? content.subscribers : [];
    const idx = list.findIndex((s) => (s.email || "").toLowerCase() === email);
    if (idx < 0) return json({ code: 404, message: "未找到该订阅者" }, 404);
    list.splice(idx, 1);
    await ghWriteFile(env, "subscribers.json", { subscribers: list }, sha, `chore: remove subscriber ${email}`);
    return json({ code: 200, message: "已取消订阅" });
  } catch (e) {
    return json({ code: 500, message: "取消订阅失败：" + (e && e.message ? e.message : e) }, 500);
  }
}
