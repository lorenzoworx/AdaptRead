# Interview guide

## One-minute pitch

AdaptRead asks which safe presentation preset should come next given recent
reading behavior. It is a contextual-bandit engineering testbed trained only on
seeded simulated readers. Hard constraints filter actions; a bounded reward
scores outcomes; random, default, and fixed-oracle baselines ground the result;
UCB1 exposes the mixed-reader compromise; and LinUCB can condition on context.

## Equations

```text
reward = comprehension + 0.5·speed − 0.35·strain − 0.15·switch_cost
UCB1(a) = mean(a) + sqrt(exploration · log(total + 1) / pulls(a))
LinUCB(a) = θₐᵀx + α sqrt(xᵀ Aₐ⁻¹ x)
```

## Current limitations

- Synthetic results cannot establish accessibility or clinical efficacy.
- Persona parameters and reward weights encode assumptions.
- Six presets omit real interface nuance.
- LinUCB assumes linear expected reward for each action.
- Specialized and held-out profiles retain meaningful regret.

## Questions to expect

**Why not deep RL?** There is no evidence this scope needs it; the contextual
model is easier to falsify and explain.

**Why an oracle?** It provides the best fixed action under paired seeds, turning
“better” into measurable regret.

**What would real validation require?** Participatory design, accessibility
expertise, consented data, appropriate ethical review, and real-reader studies.
