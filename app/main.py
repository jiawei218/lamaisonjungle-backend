from fastapi import FastAPI, Depends
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.plants import router as plants_router
from app.db.session import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.rag import router as rag_router

app = FastAPI(
    title="La Maison Jungle API",
    description="La Maison Jungle 植物商城与智能问答后端",
    version="0.1.0",
)

#计算静态文件绝对路径
APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录
app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

# 把 app/api/plants.py 中定义的接口加入主应用
app.include_router(plants_router)
app.include_router(rag_router)

@app.get("/")
def root():
    return {
        "name": "La Maison Jungle API",
        "version": "0.1.0",
    }


@app.get("/api/health")
def health_check(
    db: Session = Depends(get_db),
):
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "connected",
    }

