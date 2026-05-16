from pathlib import Path

from app.domain.entities import KnowledgeDocument
from app.domain.enums import DocumentStatus


def load_markdown_documents(base_path: str) -> list[KnowledgeDocument]:
    path = Path(base_path)
    if not path.exists():
        return []

    documents: list[KnowledgeDocument] = []
    for file_path in sorted(path.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")
        title = content.splitlines()[0].lstrip("# ").strip() if content.splitlines() else file_path.stem
        documents.append(
            KnowledgeDocument(
                id=file_path.stem,
                title=title,
                category="suporte",
                channel="both",
                version="1.0",
                status=DocumentStatus.ACTIVE,
                source=str(file_path),
                owner="suporte",
                sensitivity="interno",
                content=content,
                tags=[],
            )
        )
    return documents
