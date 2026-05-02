import { BarChart3, FileText, MessageSquareText, Rows3, type LucideIcon } from "lucide-react";
import { useState } from "react";

import { ChatPage } from "./pages/ChatPage";
import { DocumentsPage } from "./pages/DocumentsPage";
import { HistoryPage } from "./pages/HistoryPage";
import { MetricsPage } from "./pages/MetricsPage";

type View = "chat" | "history" | "documents" | "metrics";

const navItems: Array<{ id: View; label: string; icon: LucideIcon }> = [
  { id: "chat", label: "Chat", icon: MessageSquareText },
  { id: "history", label: "Historico", icon: Rows3 },
  { id: "documents", label: "Documentos", icon: FileText },
  { id: "metrics", label: "Indicadores", icon: BarChart3 }
];

export function App() {
  const [view, setView] = useState<View>("chat");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">AI</span>
          <span>AssistAI</span>
        </div>
        <nav className="nav-list" aria-label="Navegacao principal">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={view === item.id ? "nav-item active" : "nav-item"}
                onClick={() => setView(item.id)}
                type="button"
                title={item.label}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="main-panel">
        {view === "chat" && <ChatPage />}
        {view === "history" && <HistoryPage />}
        {view === "documents" && <DocumentsPage />}
        {view === "metrics" && <MetricsPage />}
      </main>
    </div>
  );
}
