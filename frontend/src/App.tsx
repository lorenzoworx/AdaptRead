import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { api } from "./api";
import { simulateTelemetry } from "./simulator";
import { blockedReason, changedSettings, readingStyle } from "./presentation";
import type { Action, Simulator, StepResponse } from "./types";

const passage = [
  "At first, adaptation looks like a design problem: choose a readable typeface, a comfortable size, and sensible spacing.",
  "But a single setting cannot suit every moment. Reading speed, pauses, regressions, and comprehension form a stream of clues. AdaptRead treats each safe presentation as an action and learns which one works best in context.",
  "This demonstration uses synthetic reader profiles. It is an engineering testbed—not evidence about people, disability, or accessibility outcomes.",
];
const settingNames = { font_size: "Text size", font_family: "Typeface", line_spacing: "Line spacing", chunk_size: "Chunk size", tts_rate: "Text to speech", theme: "Theme" };
function Sparkline({ values }: { values: number[] }) {
  const low = Math.min(0, ...values), high = Math.max(1, ...values);
  const points = values.length < 2 ? "0,55 100,55" : values.map((value, index) => `${index / (values.length - 1) * 100},${60 - (value - low) / (high - low) * 55}`).join(" ");
  return <svg className="spark" viewBox="0 0 100 65" role="img" aria-label="Reward history"><polyline points={points} /></svg>;
}

export default function App() {
  const [data, setData] = useState<Simulator | null>(null);
  const [personaId, setPersonaId] = useState("typical");
  const [sessionId, setSessionId] = useState("");
  const [action, setAction] = useState<Action | null>(null);
  const [previous, setPrevious] = useState<Action | null>(null);
  const [step, setStep] = useState(0);
  const [history, setHistory] = useState<number[]>([]);
  const [latest, setLatest] = useState<StepResponse | null>(null);
  const [minFont, setMinFont] = useState(16);
  const [ttsAllowed, setTtsAllowed] = useState(true);
  const [running, setRunning] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const inFlight = useRef(false), generation = useRef(0);
  const persona = useMemo(() => data?.personas.find((item) => item.id === personaId), [data, personaId]);

  const reset = useCallback(async () => {
    const version = ++generation.current;
    setRunning(false); setBusy(true); setError("");
    try {
      const created = await api.createSession({ min_font_size: minFont, tts_allowed: ttsAllowed, max_changed_dimensions: 2 });
      if (version !== generation.current) return;
      setSessionId(created.session_id); setAction(created.action); setPrevious(null);
      setStep(0); setHistory([]); setLatest(null);
    } catch (cause) {
      if (version === generation.current) setError(cause instanceof Error ? cause.message : "Could not start session");
    } finally { if (version === generation.current) setBusy(false); }
  }, [minFont, ttsAllowed]);
  useEffect(() => { api.simulator().then(setData).catch(() => setError("Could not load simulator contract")); }, []);
  useEffect(() => { if (data) void reset(); }, [data, personaId, reset]);

  const advance = useCallback(async () => {
    if (!persona || !action || !sessionId || inFlight.current) return;
    const version = generation.current;
    inFlight.current = true; setBusy(true); setError("");
    try {
      const response = await api.step(sessionId, simulateTelemetry(persona, action, step + 1));
      if (version !== generation.current) return;
      setPrevious(action); setAction(response.action); setLatest(response);
      setStep((value) => value + 1); setHistory((values) => [...values.slice(-39), response.reward]);
    } catch (cause) {
      if (version === generation.current) { setRunning(false); setError(cause instanceof Error ? cause.message : "Could not advance session"); }
    } finally { inFlight.current = false; if (version === generation.current) setBusy(false); }
  }, [action, persona, sessionId, step]);
  useEffect(() => {
    if (!running) return;
    const timer = window.setInterval(() => { void advance(); }, 850);
    return () => window.clearInterval(timer);
  }, [advance, running]);

  if (!data || !persona || !action) return <main className="loading">{error ? <><p role="alert">{error}</p><button onClick={() => window.location.reload()}>Reload the lab</button></> : "Loading the reading lab…"}</main>;
  const changes = previous ? changedSettings(previous, action) : [];
  const mean = history.length ? history.reduce((sum, value) => sum + value, 0) / history.length : null;
  const scores = latest?.preset_scores ?? [];
  const low = Math.min(0, ...scores.map((score) => score.estimate));
  const high = Math.max(1, ...scores.map((score) => score.estimate + (score.exploration_bonus ?? 0)));
  const width = (value: number) => Math.max(0, Math.min(100, (value - low) / (high - low) * 100));
  const chosen = data.presets.findIndex((preset) => changedSettings(preset, action).length === 0);

  return <div className="app"><header><a className="brand" href="#top"><span className="brandMark" aria-hidden="true">Aa</span>AdaptRead</a><div className="scope">Simulated reader lab</div><div className="headerMeta">Contextual bandit · LinUCB</div></header>
    <main id="top"><div className="notice"><strong>Simulated readers only.</strong><span>Profiles are parameters, not diagnoses. No claims about real-reader outcomes.</span></div>
      <section className="intro"><div><h1>Watch a reading policy make its choice.</h1><p>Six presentations. Explicit limits. A reason for every step.</p></div><div className="actions"><button className="primary" disabled={busy && !running} onClick={() => setRunning((value) => !value)}>{running ? "Pause session" : "Run session"}</button><button disabled={busy || running} onClick={() => void advance()}>Step once</button><button disabled={busy} onClick={() => void reset()}>Reset</button></div></section>
      {error && <div className="error" role="alert">{error}</div>}
      <section className="workspace"><aside className="controlPanel"><h2>Experiment setup</h2><label>Simulated persona<span className="persona-glyph" aria-hidden="true" data-shape={data.personas.findIndex((item) => item.id === personaId) % 3} /><select value={personaId} onChange={(event) => setPersonaId(event.target.value)}>{data.personas.map((item) => <option key={item.id} value={item.id}>{item.label}{item.split === "held_out" ? " · held out" : ""}</option>)}</select></label><label>Minimum text size<select value={minFont} onChange={(event) => setMinFont(Number(event.target.value))}>{[16, 18, 22, 28].map((n) => <option key={n}>{n}</option>)}</select></label><label className="toggleLabel">Allow text to speech<button className={`toggle ${ttsAllowed ? "on" : ""}`} onClick={() => setTtsAllowed((value) => !value)} aria-label="Toggle text to speech" aria-pressed={ttsAllowed}><span /></button></label><div className="budget"><strong>Change budget</strong><div className="tokens" aria-hidden="true">{[0, 1].map((n) => <span className={n < changes.length ? "spent" : ""} key={n}>{n < changes.length ? "✓" : n + 1}</span>)}</div><p aria-live="polite">{changes.length} of 2 allowed changes used.</p><small>Constraints are checked before the policy chooses.</small></div></aside>
        <article className={`reader theme-${action.theme}`}><div className="readerTop"><span>The glass library</span><span>Segment {String(step + 1).padStart(2, "0")}</span></div><div className="passage" style={readingStyle(action)}>{passage.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}</div><div className="settingStrip"><span>{action.font_size}px</span><span>{action.font_family}</span><span>{action.line_spacing}× spacing</span><span>{action.chunk_size} words</span><span>TTS {String(action.tts_rate)}</span></div></article>
        <aside className="telemetryPanel"><h2>Why this action</h2><span className={`status ${latest?.exploring ? "explore" : ""}`}>{latest ? latest.exploring ? "Exploring" : "Exploiting" : "Ready"}</span><h3>{data.preset_names[chosen]?.replaceAll("-", " ") ?? "Presentation"}</h3><p className="explanation">{latest?.explanation ?? "Start the session to see the policy's explanation."}</p><div className="change-list">{changes.length ? changes.map((key) => <div key={key}><span>{settingNames[key]}</span><strong>{String(previous![key])} → {String(action[key])}</strong></div>) : <p>No setting changes in this step.</p>}</div><div className="metric"><span>Latest reward</span><strong>{latest ? latest.reward.toFixed(3) : "—"}</strong></div><div className="chart"><div className="chartHead"><span>Reward history</span><span>{history.length} {history.length === 1 ? "step" : "steps"}</span></div><Sparkline values={history} /></div><p className="mean">Mean reward {mean === null ? "—" : mean.toFixed(3)}</p></aside></section>
      <section className="bench" aria-labelledby="bench-title"><div className="bench-heading"><h2 id="bench-title">The presentation bench</h2><p>Six actual presets. Blocked choices never reach the policy.</p></div><div className="specimens">{data.presets.map((preset, index) => {
        const score = scores.find((item) => item.action_index === index);
        const reason = blockedReason(preset, previous ?? action, minFont, ttsAllowed);
        const blocked = score ? !score.allowed : Boolean(reason);
        return <article key={index} className={`specimen ${index === chosen ? "chosen" : ""} ${blocked ? "blocked" : ""} specimen-${index}`} aria-label={`${data.preset_names[index]}${index === chosen ? ", chosen" : ""}${blocked ? ", blocked" : ""}`}><h3>{data.preset_names[index]?.replaceAll("-", " ")}</h3><div className={`specimen-text theme-${preset.theme}`} style={readingStyle(preset)}>A clear<br />next step.</div><p>{preset.font_size}px · {preset.font_family}<br />{preset.chunk_size}-word chunks · TTS {String(preset.tts_rate)}</p>{score && !blocked ? <><div className="score-track" role="img" aria-label={`Estimated reward ${score.estimate.toFixed(3)}, exploration bonus ${score.exploration_bonus?.toFixed(3) ?? "untried"}`}><i style={{ width: `${width(score.estimate)}%` }} /><span style={{ left: `${width(score.estimate)}%`, width: `${width(score.estimate + (score.exploration_bonus ?? 0)) - width(score.estimate)}%` }} /></div><small>Estimate {score.estimate.toFixed(2)}<br />Bonus {score.exploration_bonus === null ? "untried" : score.exploration_bonus.toFixed(2)}</small></> : <small>{blocked ? `Blocked: ${reason ?? "safety constraint"}` : "Awaiting a policy step"}</small>}</article>;
      })}</div><p className="score-note">Bars show relative reward estimates; whiskers show the policy's exploration bonus. These are not confidence probabilities. {previous && "The displayed mask is for the decision from the previous presentation."}</p></section>
      <section className="how"><div><h2>Observe</h2><p>Behavior becomes seven observable features.</p></div><div><h2>Choose safely</h2><p>Filter constraints, then score allowed presets.</p></div><div><h2>Learn locally</h2><p>Session updates are isolated and discarded when the session ends.</p></div></section>
    </main><footer><span>AdaptRead / Portfolio testbed</span><span>No claims about real-reader outcomes</span></footer></div>;
}
