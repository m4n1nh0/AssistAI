import { RefreshCcw } from "lucide-react";
import { useEffect, useState } from "react";

import type { DocumentResponse } from "../../domain/contracts";
import { apiClient } from "../../infrastructure/api/client";

export function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);

  async function load() {
    setDocuments(await apiClient.listDocuments());
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <section className="workspace">
      <header className="workspace-header">
        <div>
          <h1>Documentos</h1>
          <p>Base de conhecimento disponivel para RAG.</p>
        </div>
        <button className="icon-button" onClick={() => void load()} type="button" title="Atualizar">
          <RefreshCcw size={16} />
        </button>
      </header>

      <div className="document-grid">
        {documents.map((document) => (
          <article className="document-item" key={document.document_id}>
            <h2>{document.title}</h2>
            <dl>
              <div>
                <dt>Categoria</dt>
                <dd>{document.category}</dd>
              </div>
              <div>
                <dt>Versao</dt>
                <dd>{document.version}</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>{document.status}</dd>
              </div>
            </dl>
          </article>
        ))}
      </div>
    </section>
  );
}

