# Decisions

## Contextual bandit, not full reinforcement learning

The next presentation depends on recent observable behavior, but version one
does not claim to solve long-horizon credit assignment. A contextual bandit is
easier to inspect, more data-efficient, and proportionate to the evidence.

## Six curated presets

The full product contains 2,160 combinations, many difficult to explain or
explore safely. Six coherent presets make exhaustive fixed baselines practical.

## Hard constraints before optimization

Minimum font size, TTS permission, and the two-dimension transition limit are
filters. A reward penalty could still permit a prohibited exploratory action.

## Bounded reward

Every term is clipped before weighting. This preserves the declared
`[-0.5, 1.5]` contract and prevents telemetry outliers from dominating.

## Paired, frozen evaluation

Policy and oracle share evaluation seeds. Learning and exploration are disabled
without changing counters. Multiple training seeds, bootstrap intervals,
per-persona regret, and held-out regret remain visible even when results are
negative or mixed.

## JSON policy artifacts

JSON is inspectable, portable, and schema-versioned. Unlike pickle, loading it
does not execute arbitrary Python. Artifacts record model parameters plus the
configuration hash, training seeds, creation time, and evaluation summary.

## Ephemeral, isolated serving

Each session clones the persisted policy and updates only its copy. The store
is bounded and in-memory, making restarts intentionally discard synthetic live
learning. Serving-time strain is estimated from regressions and pauses; that
proxy is acknowledged train/serve skew rather than presented as latent fatigue.

## API-owned demo parameters

The React app does not carry a handwritten copy of presets or persona
parameters. It fetches them from the API, preventing the visualization from
silently diverging from the experiment. The UI repeatedly identifies all
behavior as simulated.

## One stateless production service

The production image serves the compiled client and API from one process and
one origin. This keeps the portfolio deployment small and avoids cross-origin
configuration. Render's free tier may spin the service down while idle and its
filesystem is ephemeral. That is acceptable because live sessions are bounded,
synthetic, and explicitly disposable; a real product would move session state
to durable storage and define privacy, deletion, and migration policies.

Deployments wait for repository checks rather than triggering immediately on
every commit. The same image-level health endpoint is also configured as the
platform health gate.
