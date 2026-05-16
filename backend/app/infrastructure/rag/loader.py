import uuid
from typing import Iterator

from app.domain.enums import DocumentStatus
from app.domain.models import KnowledgeDocument, utc_now


class MarkdownLoader:
    """Carrega dados de arquivos Markdown para a entidade de domínio."""

    def load(self, file_path: str, category: str = "general") -> KnowledgeDocument:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        filename = file_path.split("/")[-1]
        
        return KnowledgeDocument(
            id=uuid.uuid4().hex,
            title=filename,
            category=category,
            channel="all",
            version="1.0",
            status=DocumentStatus.ACTIVE,
            updated_at=utc_now(),
            source=file_path,
            owner="system",
            sensitivity="internal",
            content=content,
            tags=[]
        )
