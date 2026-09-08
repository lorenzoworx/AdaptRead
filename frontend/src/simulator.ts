import type { Action, Persona } from "./types";

const fields: (keyof Action)[] = ["font_size", "font_family", "line_spacing", "chunk_size", "tts_rate", "theme"];

export function simulateTelemetry(persona: Persona, action: Action, step: number) {
  const fit = 1 - fields.filter((field) => action[field] !== persona.preferred_action[field]).length / fields.length;
  const wave = Math.sin(step * 1.71 + persona.base_wpm) * 0.025;
  const fatigue = Math.min(0.75, step * persona.fatigue_rate * 0.3);
  const difficulty = 0.36 + ((step * 17) % 41) / 100;
  const strain = Math.max(0.02, Math.min(0.92, difficulty * (1.05 - fit) + fatigue));
  const probability = 1 / (1 + Math.exp(-(persona.comprehension_bias + 2.2 * fit - 2.4 * strain)));
  return {
    observed_wpm: Math.max(40, persona.base_wpm * (0.75 + 0.4 * fit) * (1 - 0.3 * fatigue) * (1 + wave)),
    regression_rate: Math.max(0, Math.min(1, 0.05 + strain * 0.5 + wave)),
    pause_ratio: Math.max(0, Math.min(1, 0.03 + strain * 0.42 - wave)),
    probe_correct: probability > 0.5 ? 1 : 0,
    segment_difficulty: difficulty,
    segment_length: 0.3 + ((step * 11) % 53) / 100,
  };
}
