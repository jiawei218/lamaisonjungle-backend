from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from pytest import MonkeyPatch

from app.services import rag


def test_rag_uses_retrieved_context(monkeypatch: MonkeyPatch) -> None:
    seen: list[str] = []

    class FakeVectorSearch:
        def get_retriever(self) -> RunnableLambda:
            return RunnableLambda(
                lambda question: [Document(page_content="每周浇水一次", metadata={"source": "plant.txt"})]
            )

    def fake_model(prompt: object) -> AIMessage:
        content = prompt.to_string()
        seen.append(content)
        return AIMessage(content="根据资料，每周浇水一次")

    monkeypatch.setattr(rag, "VectorSearchService", FakeVectorSearch)
    monkeypatch.setattr(rag, "ChatOpenAI", lambda **kwargs: RunnableLambda(fake_model))

    answer = rag.RAGService().chain.invoke("龟背竹多久浇水？")

    assert answer == "根据资料，每周浇水一次"
    assert "龟背竹多久浇水？" in seen[0]
    assert "每周浇水一次" in seen[0]
    assert "plant.txt" in seen[0]


def test_rag_supplies_no_context_marker(monkeypatch: MonkeyPatch) -> None:
    seen: list[str] = []

    class EmptyVectorSearch:
        def get_retriever(self) -> RunnableLambda:
            return RunnableLambda(lambda question: [])

    def fake_model(prompt: object) -> AIMessage:
        seen.append(prompt.to_string())
        return AIMessage(content="目前不清楚")

    monkeypatch.setattr(rag, "VectorSearchService", EmptyVectorSearch)
    monkeypatch.setattr(rag, "ChatOpenAI", lambda **kwargs: RunnableLambda(fake_model))

    assert rag.RAGService().chain.invoke("未知问题") == "目前不清楚"
    assert "无相关参考资料" in seen[0]
