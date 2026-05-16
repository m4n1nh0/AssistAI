import { useCallback } from "react";

import { apiClient } from "../../infrastructure/apiClient";
import { EmptyState } from "../components/EmptyState";
import { useApiResource } from "../../application/useApiResource";

export function HistoryView() {
  const loadAttendances = useCallback(() => apiClient.listAttendances(), []);
  const { data, isLoading, error } = useApiResource(loadAttendances);

  return (
    <div className="workspace">
      <header className="workspace-header">
        <div>
          <p>Rastreabilidade</p>
          <h1>Histórico de atendimentos</h1>
        </div>
      </header>

      {isLoading && <span className="typing">Carregando histórico...</span>}
      {error && <span className="error-text">{error}</span>}
      {!isLoading && data?.items.length === 0 && (
        <EmptyState title="Nenhum atendimento registrado" description="As conversas aparecerão aqui após o primeiro envio." />
      )}

      <div className="data-grid">
        {data?.items.map((attendance) => (
          <article className="data-row" key={attendance.id}>
            <strong>{attendance.user_id}</strong>
            <span>{attendance.channel}</span>
            <span>{attendance.total_messages} mensagem(ns)</span>
            <small>{new Date(attendance.created_at).toLocaleString("pt-BR")}</small>
          </article>
        ))}
      </div>
    </div>
  );
}
