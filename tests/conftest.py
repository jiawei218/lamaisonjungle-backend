import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool


# Settings is created while app modules are imported. These test values must
# therefore be present before importing the application.
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "3306"
os.environ["DB_USER"] = "test"
os.environ["DB_PASSWORD"] = "test"
os.environ["DB_NAME"] = "test"
os.environ["DASHSCOPE_API_KEY"] = "test-key"
os.environ["DASHSCOPE_BASE_URL"] = "https://example.invalid/v1"
os.environ["DASHSCOPE_MODEL"] = "test-model"
os.environ["PATH_MD5_FILE"] = "app/static/md5.txt"
os.environ["CHROMA_COLLECTION_NAME"] = "test-collection"
os.environ["CHROMA_EMBEDDING_MODEL"] = "test-embedding"
os.environ["CHROMA_PERSIST_DIRECTORY"] = "app/chroma_db"


from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Plant  # noqa: F401 - registers the model metadata


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

Base.metadata.create_all(test_engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(
    db_session: Session,
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
