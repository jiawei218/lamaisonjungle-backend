from pathlib import Path

import pytest
from pytest import MonkeyPatch

from app.core.config import settings
from app.services.knowledge_base import KnowledgeBaseService, check_md5, project_path, save_md5


def test_relative_paths_use_project_root(tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    assert project_path("./app/static/md5.txt") == (
        Path(__file__).resolve().parents[1] / "app/static/md5.txt"
    )


def test_chroma_path_is_under_project_app_when_started_from_services(
    monkeypatch: MonkeyPatch,
) -> None:
    project_root = Path(__file__).resolve().parents[1]
    monkeypatch.chdir(project_root / "app/services")

    assert project_path("./app/chroma_db") == project_root / "app/chroma_db"


def test_md5_file_is_created_with_parent_directories(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    md5_file = tmp_path / "nested" / "md5.txt"
    monkeypatch.setattr(settings, "path_md5_file", str(md5_file))

    assert check_md5("example-hash") is False
    assert md5_file.is_file()

    save_md5("example-hash")
    assert check_md5("example-hash") is True


def test_embedding_file_stores_chunks_and_skips_duplicate(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "path_md5_file", str(tmp_path / "md5.txt"))
    monkeypatch.setattr(settings, "max_spliter_char_number", 3)
    stored: list[tuple[list[str], list[dict[str, str]]]] = []

    class FakeChroma:
        def add_texts(self, texts: list[str], metadatas: list[dict[str, str]]) -> None:
            stored.append((texts, metadatas))

    service = KnowledgeBaseService.__new__(KnowledgeBaseService)
    service.chroma = FakeChroma()
    service.spliter = type("Splitter", (), {"split_text": lambda self, text: ["植物", "养护"]})()

    assert service.embedding_file("植物养护", "plants.txt").startswith("[成功]")
    assert service.embedding_file("植物养护", "plants.txt").startswith("[跳过]")
    assert len(stored) == 1
    assert stored[0][0] == ["植物", "养护"]
    assert [item["source"] for item in stored[0][1]] == ["plants.txt", "plants.txt"]


def test_short_document_is_stored_without_splitting(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    monkeypatch.setattr(settings, "path_md5_file", str(tmp_path / "md5.txt"))
    monkeypatch.setattr(settings, "max_spliter_char_number", 300)
    stored: list[list[str]] = []

    class FakeChroma:
        def add_texts(self, texts: list[str], metadatas: list[dict[str, str]]) -> None:
            stored.append(texts)

    service = KnowledgeBaseService.__new__(KnowledgeBaseService)
    service.chroma = FakeChroma()
    service.spliter = type("Splitter", (), {"split_text": lambda self, text: pytest.fail("split called")})()

    service.embedding_file("公司介绍", "company.txt")

    assert stored == [["公司介绍"]]
