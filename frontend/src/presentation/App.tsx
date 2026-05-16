import { BarChart3, FileText, History, MessageSquare } from "lucide-react";
import type { ComponentType } from "react";
import { useState } from "react";

import { ChatView } from "./views/ChatView";
import { DocumentsView } from "./views/DocumentsView";
import { HistoryView } from "./views/HistoryView";
import { MetricsView } from "./views/MetricsView";

type View = "chat" | "history" | "documents" | "metrics";

const views: Array<{ id: View; label: string; icon: ComponentType<{ size?: number }> }> = [
  { id: "chat", label: "Chat", icon: MessageSquare },
  { id: "history", label: "Histórico", icon: History },
  { id: "documents", label: "Documentos", icon: FileText },
  { id: "metrics", label: "Indicadores", icon: BarChart3 }
];

export function App() {
  const [activeView, setActiveView] = useState<View>("chat");

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">AI</span>
          <div>
            <strong>Atendimento</strong>
            <span>POC RAG</span>
          </div>
        </div>

        <nav className="nav-list" aria-label="Navegação principal">
          {views.map((view) => {
            const Icon = view.icon;
            return (
              <button
                key={view.id}
                className={activeView === view.id ? "nav-item active" : "nav-item"}
                type="button"
                onClick={() => setActiveView(view.id)}
              >
                <Icon size={18} />
                <span>{view.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <section className="content">
        {activeView === "chat" && <ChatView />}
        {activeView === "history" && <HistoryView />}
        {activeView === "documents" && <DocumentsView />}
        {activeView === "metrics" && <MetricsView />}
      </section>
    </main>
  );
}
