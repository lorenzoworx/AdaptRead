import { expect, test } from "vitest";
import { blockedReason, changedSettings, readingStyle } from "./presentation";
import type { Action } from "./types";
const base: Action = { font_size: 18, font_family: "sans", line_spacing: 1.6, chunk_size: 20, tts_rate: "off", theme: "light" };
test("counts actual dimensions and blocks unsafe transitions", () => {
  const low: Action = { ...base, font_size: 28, theme: "dark" };
  expect(changedSettings(base, low)).toEqual(["font_size", "theme"]);
  expect(blockedReason(low, base, 18, true)).toBeNull();
  expect(blockedReason({ ...low, font_family: "opendyslexic" }, base, 18, true)).toMatch(/3 changes/);
  expect(blockedReason(base, low, 22, true)).toMatch(/minimum/);
  expect(blockedReason({ ...base, tts_rate: 1 }, base, 18, false)).toMatch(/disabled/);
});
test("OpenDyslexic presets use their real font", () => {
  expect(readingStyle({ ...base, font_family: "opendyslexic" }).fontFamily).toContain("OpenDyslexic");
});
