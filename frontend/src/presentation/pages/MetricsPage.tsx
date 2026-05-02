import { RefreshCcw } from "lucide-react";
import { useEffect, useState } from "react";

import type { MetricSummary } from "../../domain/contracts";
import { apiClient } from "../../infrastructure/api/client";

export function MetricsPage() {
  const [metrics, setMetrics] = useState<MetricSummary | null>(null);

  async function load() {
    setMetrics(await apiClient.metrics());
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <section className="workspace">
      <header className="workspace-header">
        <div>
          <h1>Indicadores</h1>
          <p>Resumo operacional da POC.</p>
        </div>
        <button className="icon-button" onClick={() => void load()} type="button" title="Atualizar">
          <RefreshCcw size={16} />
        </button>
      </header>

      {metrics && (
        <div className="metric-grid">
          <div className="metric-item">
            <span>Atendimentos</span>
            <strong>{metrics.total_attendances}</strong>
          </div>
          <div className="metric-item">
            <span>Mensagens</span>
            <strong>{metrics.total_messages}</strong>
          </div>
          <div className="metric-item">
            <span>Fallback</span>
            <strong>{Math.round(metrics.fallback_rate * 100)}%</strong>
          </div>
          <div className="metric-item">
            <span>Feedback util</span>
            <strong>{Math.round(metrics.useful_feedback_rate * 100)}%</strong>
          </div>
        </div>
      )}
    </section>
  );
}

