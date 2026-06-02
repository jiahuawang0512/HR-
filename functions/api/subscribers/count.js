// EdgeOne Pages Function: 订阅人数
// 路径：GET /api/subscribers/count

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": "*",
      "cache-control": "no-store",
    },
  });
}

export async function onRequestGet(context) {
  const { env } = context;
  try {
    // 直接读公网 raw 文件，免 token、零延迟
    const repo = env.GITHUB_REPO || "";
    const branch = env.GITHUB_BRANCH || "main";
    const url = repo
      ? `https://raw.githubusercontent.com/${repo}/${branch}/subscribers.json`
      : "/subscribers.json";
    const r = await fetch(url, { cf: { cacheTtl: 30 } });
    if (!r.ok) throw new Error("read subscribers.json failed");
    const data = await r.json();
    const list = Array.isArray(data.subscribers) ? data.subscribers : [];
    const count = list.filter((s) => s.active !== false).length;
    return json({ code: 200, data: { count } });
  } catch (e) {
    return json({ code: 200, data: { count: 0 } });
  }
}
