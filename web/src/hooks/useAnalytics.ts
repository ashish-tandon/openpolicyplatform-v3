export type AnalyticsEvent = { name: string; props?: Record<string, any> };

export function useAnalytics() {
  const enabled = (import.meta as any).env?.VITE_ENABLE_ANALYTICS === 'true';
  async function track(event: AnalyticsEvent) {
    if (!enabled) return;
    try {
      await fetch('/api/v1/metrics', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(event) });
    } catch { /* ignore */ }
  }
  return { track };
}