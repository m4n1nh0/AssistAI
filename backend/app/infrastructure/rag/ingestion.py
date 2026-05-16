from app.infrastructure.rag.loader import MarkdownLoader
from app.infrastructure.rag.chunker import MarkdownChunker
from app.infrastructure.vector.qdrant import QdrantConfig, QdrantVectorStore

import os
from dotenv import load_dotenv

load_dotenv()


def main():
    print("Iniciando pipeline de ingestão...")

    # Load from Knowledge Base
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../knowledge_base"))
    file_path = os.path.join(base_dir, "suporte_interno.md")
    
    loader = MarkdownLoader()
    doc = loader.load(file_path)
    print(f"Documento '{doc.title}' carregado.")
    
    # Chunking
    chunker = MarkdownChunker()
    chunks = chunker.chunk(doc)
    print(f"Documento fragmentado em {len(chunks)} chunks.")
    
    # Qdrant Upsert
    qdrant_url = os.getenv("ASSISTAI_QDRANT_URL", "http://localhost:6333")
    config = QdrantConfig(url=qdrant_url, collection="assistai_knowledge")
    store = QdrantVectorStore(config)
    
    print(f"Enviando chunks para o Qdrant em {qdrant_url}...")
    upserted = store.upsert_chunks(chunks)
    print(f"Sucesso! {upserted} chunks inseridos/atualizados na coleção '{config.collection}'.")
    

if __name__ == "__main__":
    main()
