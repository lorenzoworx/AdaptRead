import type { Action } from "./types";
export const dimensions = ["font_size", "font_family", "line_spacing", "chunk_size", "tts_rate", "theme"] as const;
export function changedSettings(previous: Action, next: Action) {
  return dimensions.filter((key) => previous[key] !== next[key]);
}
export function blockedReason(preset: Action, previous: Action, minFont: number, tts: boolean) {
  if (preset.font_size < minFont) return `Below ${minFont}px minimum`;
  if (!tts && preset.tts_rate !== "off") return "Text to speech disabled";
  const count = changedSettings(previous, preset).length;
  return count > 2 ? `${count} changes; limit is 2` : null;
}
export function readingStyle(action: Action) {
  return { fontFamily: action.font_family === "opendyslexic" ? "OpenDyslexic, sans-serif" : action.font_family === "serif" ? "Georgia, serif" : "Plex, sans-serif", fontSize: `${action.font_size}px`, lineHeight: action.line_spacing };
}
