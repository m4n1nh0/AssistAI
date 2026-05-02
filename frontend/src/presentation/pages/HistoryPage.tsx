import { RefreshCcw } from "lucide-react";
import { useEffect, useState } from "react";

import type { AttendanceListItem } from "../../domain/contracts";
import { apiClient } from "../../infrastructure/api/client";

export function HistoryPage() {
  const [items, setItems] = useState<AttendanceListItem[]>([]);

  async function load() {
    setItems(await apiClient.listAttendances());
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <section className="workspace">
      <header className="workspace-header">
        <div>
          <h1>Historico</h1>
          <p>Atendimentos registrados pela API.</p>
        </div>
        <button className="icon-button" onClick={() => void load()} type="button" title="Atualizar">
          <RefreshCcw size={16} />
        </button>
      </header>

      <div className="data-table">
        <div className="table-row table-head">
          <span>ID</span>
          <span>Canal</span>
          <span>Mensagens</span>
          <span>Status</span>
        </div>
        {items.map((item) => (
          <div className="table-row" key={item.attendance_id}>
            <span>{item.attendance_id}</span>
            <span>{item.channel}</span>
            <span>{item.message_count}</span>
            <span>{item.escalated ? "Escalonado" : "Automatizado"}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

