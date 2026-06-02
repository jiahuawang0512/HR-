// EdgeOne Pages Function: 系统状态（stub）
// 路径：GET /api/admin/status

function json(body) {
  return new Response(JSON.stringify(body), {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": "*",
      "cache-control": "no-store",
    },
  });
}

export async function onRequestGet() {
  return json({
    code: 200,
    data: {
      status: "running",
      scheduler: "running",
      message: "由 GitHub Actions 每日定时调度",
      next_fetch: "每天 10:15 / 18:30 (Asia/Shanghai)",
    },
  });
}
