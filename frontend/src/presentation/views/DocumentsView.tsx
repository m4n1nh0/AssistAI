import { FormEvent, useCallback, useState } from "react";

import { useApiResource } from "../../application/useApiResource";
import type { DocumentCreateRequest, ReindexResponse } from "../../domain/types";
import { apiClient } from "../../infrastructure/apiClient";
import { EmptyState } from "../components/EmptyState";

const initialForm: DocumentCreateRequest = {
  title: "",
  category: "suporte",
  content: "",
  channel: "both",
  version: "1.0",
  status: "active",
  source: "manual",
  owner: "suporte",
  sensitivity: "interno",
  tags: []
};

export function DocumentsView() {
  const loadDocuments = useCallback(() => apiClient.listDocuments(), []);
  const { data, isLoading, error, refresh } = useApiResource(loadDocuments);
  const [form, setForm] = useState<DocumentCreateRequest>(initialForm);
  const [tagsInput, setTagsInput] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [reindexResult, setReindexResult] = useState<ReindexResponse | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setActionError(null);

    try {
      await apiClient.createDocument({
        ...form,
        tags: tagsInput
          .split(",")
          .map((tag) => tag.trim())
          .filter(Boolean)
      });
      setForm(initialForm);
      setTagsInput("");
      await refresh();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Erro ao cadastrar documento.");
    } finally {
      setIsSaving(false);
    }
  }

  async function handleReindex() {
    setActionError(null);

    try {
      setReindexResult(await apiClient.reindexDocuments());
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "Erro ao reindexar documentos.");
    }
  }

  return (
    <div className="workspace">
      <header className="workspace-header">
        <div>
          <p>Base de conhecimento</p>
          <h1>Documentos</h1>
        </div>
        <button className="secondary-button" type="button" onClick={() => void handleReindex()}>
          Reindexar
        </button>
      </header>

      {isLoading && <span className="typing">Carregando documentos...</span>}
      {error && <span className="error-text">{error}</span>}
      {actionError && <span className="error-text">{actionError}</span>}
      {reindexResult && (
        <span className="success-text">
          {reindexResult.indexed_documents} documento(s), {reindexResult.indexed_chunks} chunk(s) preparados.
        </span>
      )}

      <form className="document-form" onSubmit={handleSubmit}>
        <div className="form-row">
          <label>
            Titulo
            <input
              required
              value={form.title}
              onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
            />
          </label>
          <label>
            Categoria
            <input
              required
              value={form.category}
              onChange={(event) => setForm((current) => ({ ...current, category: event.target.value }))}
            />
          </label>
        </div>

        <label>
          Conteudo
          <textarea
            required
            rows={6}
            value={form.content}
            onChange={(event) => setForm((current) => ({ ...current, content: event.target.value }))}
          />
        </label>

        <div className="form-row">
          <label>
            Versao
            <input
              value={form.version}
              onChange={(event) => setForm((current) => ({ ...current, version: event.target.value }))}
            />
          </label>
          <label>
            Tags
            <input
              value={tagsInput}
              onChange={(event) => setTagsInput(event.target.value)}
              placeholder="senha, acesso, chamado"
            />
          </label>
          <label>
            Status
            <select
              value={form.status}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  status: event.target.value as DocumentCreateRequest["status"]
                }))
              }
            >
              <option value="active">active</option>
              <option value="draft">draft</option>
              <option value="inactive">inactive</option>
            </select>
          </label>
        </div>

        <button className="primary-button" type="submit" disabled={isSaving}>
          {isSaving ? "Salvando..." : "Cadastrar documento"}
        </button>
      </form>

      {!isLoading && data?.items.length === 0 && (
        <EmptyState title="Nenhum documento encontrado" description="Cadastre um conteudo inicial para alimentar o RAG." />
      )}

      <div className="document-list">
        {data?.items.map((document) => (
          <article className="document-item" key={document.id}>
            <div>
              <strong>{document.title}</strong>
              <span>
                {document.category} - v{document.version}
              </span>
            </div>
            <span className={`status-pill ${document.status}`}>{document.status}</span>
          </article>
        ))}
      </div>
    </div>
  );
}
