import logging
from functools import lru_cache

from fastapi import APIRouter, HTTPException
from openai import (RateLimitError,
                    APITimeoutError,
                    APIStatusError,
                    APIConnectionError,
                    AuthenticationError,
                    )


from app.services.rag import RAGService
from pydantic import BaseModel, ConfigDict, Field

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/rag",
    tags=["rag"],
)

class RAGRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    question: str = Field(min_length=1)
    request_id: str


class RAGResponse(BaseModel):
    answer: str
    request_id: str

@lru_cache
def get_rag_service() -> RAGService:
    return RAGService()

@router.post("",response_model=RAGResponse)
def chat_rag(request: RAGRequest) -> RAGResponse:
    request_id = request.request_id

    try:
        answer = get_rag_service().chain.invoke(request.question)
    except RateLimitError:
        logger.warning("RAG上游服务限流，request_id = %s",request_id)
        raise HTTPException(status_code=429, detail="AI服务请求过于频繁") from None
    except APITimeoutError:
        logger.warning("RAG 上游服务超时，request_id=%s", request_id)
        raise HTTPException(status_code=504, detail="AI 服务响应超时") from None
    except APIConnectionError:
        logger.exception("RAG 上游服务连接失败，request_id=%s", request_id)
        raise HTTPException(status_code=503, detail="AI 服务暂时不可用") from None
    except AuthenticationError:
        logger.exception("RAG 上游服务认证失败，request_id=%s", request_id)
        raise HTTPException(status_code=503, detail="AI 服务暂时不可用") from None
    except APIStatusError:
        logger.exception("RAG 上游服务返回错误，request_id=%s", request_id)
        raise HTTPException(status_code=502, detail="AI 服务返回错误") from None
    except Exception:
        logger.exception("RAG 处理失败，request_id=%s", request_id)
        raise HTTPException(status_code=500, detail="AI 服务暂时不可用") from None

    if not isinstance(answer, str) or not answer.strip():
        logger.error("RAG 返回空回答，request_id=%s", request_id)
        raise HTTPException(status_code=502, detail="AI 服务未返回有效回答")

    return RAGResponse(answer=answer.strip(), request_id=request_id)