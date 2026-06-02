// EdgeOne Pages Function: 整体统计
// 路径：GET /api/stats

function json(body) {
  return new Response(JSON.stringify(body), {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": "*",
      "cache-control": "no-store",
    },
  });
}

export async function onRequestGet(context) {
  const { env } = context;
  let count = 0;
  try {
    const repo = env.GITHUB_REPO || "";
    const branch = env.GITHUB_BRANCH || "main";
    if (repo) {
      const r = await fetch(
        `https://raw.githubusercontent.com/${repo}/${branch}/subscribers.json`,
        { cf: { cacheTtl: 30 } }
      );
      if (r.ok) {
        const data = await r.json();
        const list = Array.isArray(data.subscribers) ? data.subscribers : [];
        count = list.filter((s) => s.active !== false).length;
      }
    }
  } catch (_) {}

  return json({
    code: 200,
    data: {
      total_subscribers: count,
      total_articles: 0,
      total_pushes: 0,
    },
  });
}
