"use client";

import { useEffect, useState } from "react";

type HealthState = {
  status: "checking" | "online" | "offline";
  latencyMs: number | null;
  service: string;
};

export function SystemStatus({ compact = false }: { compact?: boolean }) {
  const [health, setHealth] = useState<HealthState>({
    status: "checking",
    latencyMs: null,
    service: "系統檢查中"
  });

  useEffect(() => {
    let isMounted = true;

    async function checkHealth() {
      const startedAt = performance.now();
      try {
        const response = await fetch("/health", { cache: "no-store" });
        const payload = (await response.json().catch(() => null)) as {
          status?: string;
          service?: string;
        } | null;

        if (!isMounted) return;

        if (response.ok && payload?.status === "ok") {
          setHealth({
            status: "online",
            latencyMs: Math.round(performance.now() - startedAt),
            service: payload.service ?? "智能金融資料分析 API"
          });
        } else {
          setHealth({
            status: "offline",
            latencyMs: null,
            service: "系統連線異常"
          });
        }
      } catch {
        if (!isMounted) return;
        setHealth({
          status: "offline",
          latencyMs: null,
          service: "系統連線異常"
        });
      }
    }

    void checkHealth();
    const timer = window.setInterval(checkHealth, 30000);

    return () => {
      isMounted = false;
      window.clearInterval(timer);
    };
  }, []);

  const isOnline = health.status === "online";
  const label =
    health.status === "checking"
      ? "檢查中"
      : isOnline
        ? compact
          ? "在線"
          : "系統在線"
        : "需檢查";

  return (
    <div
      className={`system-status ${isOnline ? "is-online" : ""} ${
        health.status === "offline" ? "is-offline" : ""
      }`}
      title={health.service}
      aria-live="polite"
    >
      <span className="system-status-dot" />
      <span className="system-status-label">{label}</span>
      {!compact && health.latencyMs !== null ? (
        <span className="system-status-latency">{health.latencyMs}ms</span>
      ) : null}
    </div>
  );
}
