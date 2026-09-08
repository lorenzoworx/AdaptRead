import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { simulateTelemetry } from "./simulator";
import type { Action, Simulator, StepResponse } from "./types";

const passage = [
  "At first, adaptation looks like a design problem: choose a readable typeface, a comfortable size, and sensible spacing.",
  "But a single setting cannot suit every moment. Reading speed, pauses, regressions, and comprehension form a stream of clues. AdaptRead treats each safe presentation as an action and learns which one works best in context.",
  "This demonstration uses synthetic reader profiles. It is an engineering testbed—not evidence about people, disability, or accessibility outcomes.",
];

function Sparkline({ values }: { values: number[] }) {
  const points = values.length < 2 ? "0,55 100,55" : values.map((value, index) => {
    const x = (index / (values.length - 1)) * 100;
    const y = 62 - ((value + 0.5) / 2) * 55;
    return `${x},${Math.max(3, Math.min(62, y))}`;
  }).join(" ");
  return <svg className="spark" viewBox="0 0 100 65" preserveAspectRatio="none" aria-label="Reward history"><polyline points={points} /></svg>;
}

function App() {
  const [data, setData] = useState<Simulator | null>(null);
  const [personaId, setPersonaId] = useState("typical");
  const [sessionId, setSessionId] = useState("");
  const [action, setAction] = useState<Action | null>(null);
  const [step, setStep] = useState(0);
  const [history, setHistory] = useState<number[]>([]);
  const [latest, setLatest] = useState<StepResponse | null>(null);
  const [minFont, setMinFont] = useState(16);
  const [ttsAllowed, setTtsAllowed] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  const persona = useMemo(() => data?.personas.find((item) => item.id === personaId), [data, personaId]);

  const reset = useCallback(async () => {
    try {
      setError("");
      const created = await api.createSession({ min_font_size: minFont, tts_allowed: ttsAllowed, max_changed_dimensions: 2 });
      setSessionId(created.session_id);
      setAction(created.action);
      setStep(0);
      setHistory([]);
      setLatest(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not start session");
    }
  }, [minFont, ttsAllowed]);

  useEffect(() => { api.simulator().then(setData).catch(() => setError("Could not load simulator contract")); }, []);
  useEffect(() => { if (data) void reset(); }, [data, personaId, reset]);

  const advance = useCallback(async () => {
    if (!persona || !action || !sessionId) return;
    const response = await api.step(sessionId, simulateTelemetry(persona, action, step + 1));
    setAction(response.action);
    setLatest(response);
    setStep((value) => value + 1);
    setHistory((values) => [...values.slice(-39), response.reward]);
  }, [action, persona, sessionId, step]);

  useEffect(() => {
    if (!running) return;
    const timer = window.setInterval(() => { void advance().catch(() => setRunning(false)); }, 850);
    return () => window.clearInterval(timer);
  }, [advance, running]);

  if (!data || !persona || !action) return <main className="loading">Loading the reading lab…</main>;

  const style = {
    fontFamily: action.font_family === "serif" ? "Georgia, serif" : "Inter, sans-serif",
    fontSize: `${action.font_size}px`,
    lineHeight: action.line_spacing,
  };
  const mean = history.length ? history.reduce((sum, value) => sum + value, 0) / history.length : 0;

  return (
    <div className="app">
      <header>
        <a className="brand" href="#top"><span className="brandMark">A</span><span>AdaptRead</span></a>
        <div className="scope"><i /> SIMULATED READER LAB</div>
        <div className="headerMeta">Contextual bandit · LinUCB</div>
      </header>

      <main id="top">
        <section className="intro">
          <div><p className="eyebrow">PERSONALIZATION, MADE INSPECTABLE</p><h1>A reading interface that <em>learns in context.</em></h1></div>
          <p className="lede">Explore how a contextual bandit balances safe presentation changes, observed reading behavior, and uncertainty—one synthetic segment at a time.</p>
        </section>

        <div className="notice"><strong>Simulation boundary</strong><span>{data.scope}. Profiles are parameters, not diagnoses.</span></div>
        {error && <div className="error">{error}</div>}

        <section className="workspace">
          <aside className="controlPanel">
            <div className="panelTitle"><span>Experiment controls</span><small>SESSION {sessionId.slice(0, 6).toUpperCase()}</small></div>
            <label>Simulated persona<select value={personaId} onChange={(event) => setPersonaId(event.target.value)}>{data.personas.map((item) => <option key={item.id} value={item.id}>{item.label}{item.split === "held_out" ? " · held out" : ""}</option>)}</select></label>
            <div className="constraintGrid">
              <label>Minimum text size<select value={minFont} onChange={(event) => setMinFont(Number(event.target.value))}><option>16</option><option>18</option><option>22</option><option>28</option></select></label>
              <label className="toggleLabel">Allow text to speech<button className={`toggle ${ttsAllowed ? "on" : ""}`} onClick={() => setTtsAllowed((value) => !value)} aria-label="Toggle text to speech"><span /></button></label>
            </div>
            <div className="actions"><button className="primary" onClick={() => setRunning((value) => !value)}>{running ? "Pause session" : "Run session"}</button><button onClick={() => void advance()}>Step once</button><button onClick={() => void reset()}>Reset</button></div>
            <p className="constraintNote">Safety filter: ≤ 2 setting changes per step. Constraints are enforced before the policy chooses.</p>
          </aside>

          <article className={`reader theme-${action.theme}`}>
            <div className="readerTop"><span>THE GLASS LIBRARY</span><span>SEGMENT {String(step + 1).padStart(2, "0")}</span></div>
            <div className="passage" style={style}>{passage.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}</div>
            <div className="settingStrip"><span>{action.font_size}px</span><span>{action.font_family}</span><span>{action.line_spacing}× spacing</span><span>{action.chunk_size} words</span><span>TTS {String(action.tts_rate)}</span></div>
          </article>

          <aside className="telemetryPanel">
            <div className="panelTitle"><span>Policy telemetry</span><span className={`status ${latest?.exploring ? "explore" : ""}`}>{latest?.exploring ? "EXPLORING" : "EXPLOITING"}</span></div>
            <div className="metric"><span>Latest reward</span><strong>{latest ? latest.reward.toFixed(3) : "—"}</strong></div>
            <div className="metric"><span>Mean reward</span><strong>{history.length ? mean.toFixed(3) : "—"}</strong></div>
            <div className="metric"><span>Estimated value</span><strong>{latest ? latest.estimated_value.toFixed(3) : "—"}</strong></div>
            <div className="chart"><div className="chartHead"><span>REWARD HISTORY</span><span>{history.length} STEPS</span></div><Sparkline values={history} /></div>
            <div className="why"><span>WHY THIS ACTION</span><p>{latest?.explanation ?? "Start the session to see the policy's explanation."}</p></div>
          </aside>
        </section>

        <section className="how"><p className="eyebrow">WHAT IS HAPPENING</p><div><h2>Observe</h2><p>Speed, pauses, regressions, comprehension, difficulty, and segment length become seven behavioral features.</p></div><div><h2>Choose safely</h2><p>The policy scores only presets allowed by explicit user constraints and the two-change transition limit.</p></div><div><h2>Learn locally</h2><p>Each browser session clones a persisted policy. Online updates are isolated and disappear when the session ends.</p></div></section>
      </main>
      <footer><span>AdaptRead / Portfolio testbed / 2026</span><span>No claims about real-reader outcomes</span></footer>
    </div>
  );
}

export default App;
