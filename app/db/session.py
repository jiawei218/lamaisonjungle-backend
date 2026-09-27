from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
# 建立数据库连接和 Session

# engine：管理数据库连接。
engine = create_engine(
    settings.database_url,
#pool_pre_ping=True：使用连接前先检查连接是否有效。
    pool_pre_ping=True,
    echo=False,
)

# SessionLocal：负责创建数据库会话。
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

#get_db()：让每个 FastAPI 请求获得独立 Session，请求结束自动关闭。
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()