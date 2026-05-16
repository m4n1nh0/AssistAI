from app.application.services.document_service import DocumentService


def reindex_documents() -> None:
    result = DocumentService().reindex()
    print(f"Documentos indexados: {result.indexed_documents}; chunks: {result.indexed_chunks}")
