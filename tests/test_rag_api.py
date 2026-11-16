from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from app.api import rag


@pytest.fixture
def fake_rag(monkeypatch: MonkeyPatch) -> SimpleNamespace:
    chain = SimpleNamespace(invoke=lambda question: f"回答：{question}")
    service = SimpleNamespace(chain=chain)
    monkeypatch.setattr(rag, "get_rag_service", lambda: service)
    return chain


def test_rag_returns_answer_and_request_id(client: TestClient, fake_rag: SimpleNamespace) -> None:
    response = client.post("/api/rag", json={"question": " 龟背竹怎么浇水？ ", "request_id": "req-1"})

    assert response.status_code == 200
    assert response.json() == {"answer": "回答：龟背竹怎么浇水？", "request_id": "req-1"}


@pytest.mark.parametrize("question", ["", "   "])
def test_rag_rejects_blank_question(client: TestClient, fake_rag: SimpleNamespace, question: str) -> None:
    assert client.post("/api/rag", json={"question": question, "request_id": "req-2"}).status_code == 422


def test_rag_rejects_missing_request_id(client: TestClient, fake_rag: SimpleNamespace) -> None:
    assert client.post("/api/rag", json={"question": "你好"}).status_code == 422


@pytest.mark.parametrize("answer", ["", "  ", None])
def test_rag_rejects_empty_model_answer(
    client: TestClient, fake_rag: SimpleNamespace, answer: str | None
) -> None:
    fake_rag.invoke = lambda question: answer

    response = client.post("/api/rag", json={"question": "你好", "request_id": "req-3"})

    assert response.status_code == 502
    assert response.json() == {"detail": "AI 服务未返回有效回答"}


def test_rag_hides_unexpected_error(client: TestClient, fake_rag: SimpleNamespace) -> None:
    def fail(question: str) -> str:
        raise RuntimeError("private upstream detail")

    fake_rag.invoke = fail
    response = client.post("/api/rag", json={"question": "你好", "request_id": "req-4"})

    assert response.status_code == 500
    assert response.json() == {"detail": "AI 服务暂时不可用"}
