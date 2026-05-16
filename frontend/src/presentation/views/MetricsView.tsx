import { useCallback } from "react";

import { apiClient } from "../../infrastructure/apiClient";
import { useApiResource } from "../../application/useApiResource";

export function MetricsView() {
  const loadMetrics = useCallback(() => apiClient.getMetrics(), []);
  const { data, isLoading, error } = useApiResource(loadMetrics);

  return (
    <div className="workspace">
      <header className="workspace-header">
        <div>
          <p>Qualidade e operação</p>
          <h1>Indicadores simples</h1>
        </div>
      </header>

      {isLoading && <span className="typing">Carregando indicadores...</span>}
      {error && <span className="error-text">{error}</span>}

      {data && (
        <>
          <section className="metric-grid">
            <article className="metric">
              <span>Atendimentos</span>
              <strong>{data.total_attendances}</strong>
            </article>
            <article className="metric">
              <span>Mensagens</span>
              <strong>{data.total_messages}</strong>
            </article>
            <article className="metric">
              <span>Fallback</span>
              <strong>{Math.round(data.fallback_rate * 100)}%</strong>
            </article>
            <article className="metric">
              <span>Feedback útil</span>
              <strong>{data.useful_feedback_rate === null ? "-" : `${Math.round(data.useful_feedback_rate * 100)}%`}</strong>
            </article>
          </section>

          <section className="intent-list">
            {Object.entries(data.top_intents).map(([intent, count]) => (
              <div key={intent}>
                <span>{intent}</span>
                <strong>{count}</strong>
              </div>
            ))}
          </section>
        </>
      )}
    </div>
  );
}
