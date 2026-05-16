import re
import uuid

from app.domain.models import DocumentChunk, KnowledgeDocument, utc_now


class MarkdownChunker:
    """Quebra documentos Markdown em chunks pelas divisões de cabeçalho ou parágrafos."""

    def chunk(self, document: KnowledgeDocument) -> list[DocumentChunk]:
        # Uma implementação simples quebrando por cabeçalhos markdown "## " ou parágrafos vazios duplos
        # Split blocks that start with # or ##
        blocks = re.split(r"(?=\n##?\s)", document.content)
        
        chunks = []
        for block in blocks:
            text = block.strip()
            if not text:
                continue
            
            chunks.append(
                DocumentChunk(
                    id=uuid.uuid4().hex,
                    document_id=document.id,
                    content=text,
                    metadata={"source": document.source, "title": document.title},
                    indexed_at=utc_now()
                )
            )
        
        return chunks
