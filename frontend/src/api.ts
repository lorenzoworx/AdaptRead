import type { Simulator, StepResponse } from "./types";

const apiBase = import.meta.env.BASE_URL.replace(/\/$/, "");

type Constraints = {
  min_font_size: number;
  tts_allowed: boolean;
  max_changed_dimensions: number;
};

type SessionResponse = {
  session_id: string;
  action_index: number;
  action: StepResponse["action"];
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) throw new Error(`API request failed (${response.status})`);
  return response.json() as Promise<T>;
}

export const api = {
  simulator: () => request<Simulator>(`${apiBase}/v1/simulator`),
  createSession: (constraints: Constraints) =>
    request<SessionResponse>(`${apiBase}/v1/sessions`, {
      method: "POST",
      body: JSON.stringify({ constraints }),
    }),
  step: (sessionId: string, telemetry: Record<string, number>) =>
    request<StepResponse>(`${apiBase}/v1/sessions/${sessionId}/step`, {
      method: "POST",
      body: JSON.stringify(telemetry),
    }),
};
