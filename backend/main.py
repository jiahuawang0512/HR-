# HR信息日报 - FastAPI 主入口

import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn

import config
from database import init_database
from api import router as api_router
from scheduler import start_scheduler, stop_scheduler, get_scheduler_status


# ========== 创建 FastAPI 应用 ==========
app = FastAPI(
    title=config.API_TITLE,
    version=config.API_VERSION,
    description="HR信息日报自动推送系统 API",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)


# ========== CORS 中间件 ==========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 注册路由 ==========
app.include_router(api_router, prefix="/api")


# ========== 静态文件服务（前端） ==========
# 获取前端文件路径
frontend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
index_path = os.path.join(frontend_dir, "index.html")


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    print("\n" + "=" * 50)
    print("🚀 HR信息日报系统启动中...")
    print("=" * 50)

    # 初始化数据库
    print("📦 初始化数据库...")
    init_database()
    print("   ✅ 数据库就绪")

    # 启动调度器
    print("⏰ 启动定时任务调度器...")
    start_scheduler()
    print("   ✅ 调度器已启动")

    print("\n📍 服务地址:")
    print(f"   API文档: http://localhost:8080/api/docs")
    print(f"   前端界面: http://localhost:8080/")
    print("=" * 50 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时执行"""
    print("\n🛑 正在关闭 HR信息日报系统...")
    stop_scheduler()
    print("   ✅ 系统已关闭")


# ========== 前端路由（所有非API请求返回index.html） ==========
@app.get("/")
async def serve_frontend():
    """服务前端页面"""
    return FileResponse(index_path)


@app.get("/{path:path}")
async def serve_static(path: str):
    """服务静态文件"""
    file_path = os.path.join(frontend_dir, path)

    # 安全检查：确保文件在项目目录内
    if not file_path.startswith(frontend_dir):
        return JSONResponse({"error": "Forbidden"}, status_code=403)

    if os.path.isfile(file_path):
        return FileResponse(file_path)
    else:
        # 返回 index.html（SPA 路由支持）
        return FileResponse(index_path)


# ========== 错误处理 ==========
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse({
        "code": 404,
        "message": "请求的资源不存在"
    }, status_code=404)


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse({
        "code": 500,
        "message": "服务器内部错误"
    }, status_code=500)


# ========== 启动命令 ==========
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8082,
        reload=False,  # 生产环境设为 False
        log_level="info"
    )
