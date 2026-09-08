import { render, screen } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";
import App from "./App";

afterEach(() => vi.restoreAllMocks());

test("clearly labels the demo as simulated", async () => {
  vi.stubGlobal("fetch", vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.includes("/v1/simulator")) return new Response(JSON.stringify({
      scope: "simulated readers only",
      presets: [], preset_names: [],
      personas: [{ id: "typical", label: "Typical reader", split: "training", base_wpm: 250,
        preferred_action: { font_size: 18, font_family: "sans", line_spacing: 1.6, chunk_size: 20, tts_rate: "off", theme: "light" },
        comprehension_bias: .8, fatigue_rate: .03, recovery_rate: .05 }],
    }), { status: 200 });
    return new Response(JSON.stringify({ session_id: "abc123", action_index: 0,
      action: { font_size: 18, font_family: "sans", line_spacing: 1.6, chunk_size: 20, tts_rate: "off", theme: "light" } }), { status: 201 });
  }));
  render(<App />);
  expect(await screen.findByText("SIMULATED READER LAB")).toBeInTheDocument();
  expect(await screen.findByText(/not evidence about people/i)).toBeInTheDocument();
});
