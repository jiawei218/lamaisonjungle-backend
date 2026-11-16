from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

# 应用配置
class Settings(BaseSettings):
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str
    db_password: str
    db_name: str

    dashscope_api_key: SecretStr
    dashscope_base_url: str
    dashscope_model: str

#RAG
    path_md5_file:str
    chroma_collection_name:str
    chroma_embedding_model: str
    chroma_persist_directory: str
    search_kwargs:int = 2

    #spliter
    chunk_size :int = 550
    chunk_overlap:int = 50
    separators: list[str] = ["\n\n", "\n", ".", "!", "?", "。", "！", "？", " ", ""]
    max_spliter_char_number:int = 300


    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="mysql+pymysql",
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query={"charset": "utf8mb4"},
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
