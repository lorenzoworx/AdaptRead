import type { Simulator, StepResponse } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) throw new Error(`API request failed (${response.status})`);
  return response.json() as Promise<T>;
}

export const api = {
  simulator: () => request<Simulator>("/v1/simulator"),
  createSession: (constraints: { min_font_size: number; tts_allowed: boolean; max_changed_dimensions: number }) =>
    request<{ session_id: string; action_index: number; action: StepResponse["action"] }>("/v1/sessions", {
      method: "POST",
      body: JSON.stringify({ constraints }),
    }),
  step: (sessionId: string, telemetry: Record<string, number>) =>
    request<StepResponse>(`/v1/sessions/${sessionId}/step`, {
      method: "POST",
      body: JSON.stringify(telemetry),
    }),
};
