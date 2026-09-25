"use client";

import {
  fetchAgentStatus,
  runAgentBatch,
  fetchAgentTasks,
  clearAgentTasks,
  type AgentStatus,
  type AgentRunResult,
  type AgentTasks,
} from "@/lib/api";
import { useEffect, useState } from "react";

const BATCH_SIZES = [5, 10, 20, 50];

export default function AgentPage() {
  const [status, setStatus] = useState<AgentStatus | null>(null);
  const [tasks, setTasks] = useState<AgentTasks | null>(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [batchSize, setBatchSize] = useState(10);

  const loadStatus = async () => {
    setLoading(true);
    setError(null);
    try {
      const [s, t] = await Promise.all([
        fetchAgentStatus(),
        fetchAgentTasks(),
      ]);
      setStatus(s);
      setTasks(t);
    } catch {
      setError("Gagal memuat status agent");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleRun = async () => {
    setRunning(true);
    setError(null);
    try {
      await runAgentBatch(batchSize);
      await loadStatus();
    } catch {
      setError("Gagal menjalankan agent");
      setRunning(false);
    } finally {
      setRunning(false);
    }
  };

  const handleClear = async () => {
    try {
      await clearAgentTasks();
      await loadStatus();
    } catch {
      setError("Gagal membersihkan task");
    }
  };

  return (
    <main className="agent-shell">
      <nav className="site-nav">
        <div className="nav-inner">
          <a href="/" className="brand" aria-label="PharmAI beranda">
            <span className="brand-mark">+</span>
            <span>Pharm<span>AI</span></span>
          </a>
          <div className="nav-links">
            <a href="/drugs">Database Obat</a>
            <a href="/interactions">Interaksi</a>
            <a href="/ocr">Resep</a>
            <a href="/agent" className="agent-nav-active">
              AI Agent
            </a>
          </div>
          <a href="/scan" className="nav-action">
            Mulai scan <span aria-hidden="true">↗</span>
          </a>
        </div>
      </nav>

      <section className="agent-page">
        <div className="agent-header">
          <span className="section-kicker">PHARMAI AGENT</span>
          <h1>
            AI Agent <em>Otonom.</em>
          </h1>
          <p>
            Agent ini secara otomatis menganalisis obat yang belum memiliki
            data penggunaan lengkap (indikasi, manfaat, dosis, waktu pakai,
            frekuensi) menggunakan OpenRouter AI.
          </p>
        </div>

        {error && (
          <div className="agent-error">
            <span>{error}</span>
          </div>
        )}

        <div className="agent-controls">
          <label>
            Batch size:
            <select
              value={batchSize}
              onChange={(e) => setBatchSize(Number(e.target.value))}
              disabled={running}
            >
              {BATCH_SIZES.map((size) => (
                <option key={size} value={size}>
                  {size} obat
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            className="agent-run-btn"
            onClick={handleRun}
            disabled={running || loading}
          >
            {running ? "⏳ Memproses..." : "▶ Jalankan Agent Sekarang"}
          </button>
          <button
            type="button"
            className="agent-clear-btn"
            onClick={handleClear}
            disabled={running || !tasks?.tasks?.length}
          >
            ⌁ Hapus Riwayat
          </button>
        </div>

        {loading ? (
          <div className="agent-skeleton" />
        ) : status ? (
          <div className="agent-status-card">
            <div className="status-row">
              <span>Status</span>
              <strong
                className={
                  status.running ? "status-running" : "status-idle"
                }
              >
                {status.running ? "▶ Berjalan" : "○ Idle"}
              </strong>
            </div>
            <div className="status-row">
              <span>Obat belum dianalisis</span>
              <strong>{status.unanalyzed_count?.toLocaleString("id-ID") || 0}</strong>
            </div>
            <div className="status-row">
              <span>Obat sudah dianalisis</span>
              <strong>{status.analyzed_count?.toLocaleString("id-ID") || 0}</strong>
            </div>
            <div className="status-row">
              <span>Terakhir dijalankan</span>
              <strong>
                {status.last_run
                  ? new Date(status.last_run).toLocaleString("id-ID")
                  : "Belum pernah"}
              </strong>
            </div>
            {status.current_drug && (
              <div className="status-row">
                <span>Sedang diproses</span>
                <strong>
                  {status.current_drug.name} (ID {status.current_drug.id})
                </strong>
              </div>
            )}
          </div>
        ) : null}

        {tasks && tasks.tasks && tasks.tasks.length > 0 && (
          <div className="agent-tasks">
            <h2>Riwayat Task</h2>
            <div className="task-list">
              {tasks.tasks.map((task, idx) => (
                <div
                  key={idx}
                  className={`task-item status-${task.status}`}
                >
                  <div className="task-info">
                    <span className="task-name">{task.name}</span>
                    <span className="task-id">ID {task.drug_id}</span>
                  </div>
                  <div className="task-result">
                    {task.status === "success" &&
                      task.confidence !== undefined && (
                        <span className="task-confidence">
                          {Math.round(task.confidence * 100)}%
                        </span>
                      )}
                    {task.status === "failed" && (
                      <span className="task-error">{task.error}</span>
                    )}
                    <span
                      className={`task-status-badge status-${task.status}`}
                    >
                      {task.status === "success" ? "✓" : "✗"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <div className="task-summary">
              <span>✓ {tasks.processed} berhasil</span>
              <span>✗ {tasks.failed} gagal</span>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
