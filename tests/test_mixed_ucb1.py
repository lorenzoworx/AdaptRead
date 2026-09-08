from __future__ import annotations

from adaptread.experiments.mixed_ucb1 import ComparisonConfig, run_comparison
from adaptread.simulator.personas import TRAINING_PERSONAS


def test_mixed_reader_experiment_records_specialists_and_compromise() -> None:
    config = ComparisonConfig(
        episodes=20,
        episode_length=5,
        training_seeds=(7,),
        evaluation_seeds=(31, 37),
        bootstrap_samples=100,
    )
    report = run_comparison(config)
    run = report["runs"][0]
    assert set(run["specialists"]) == {persona.id for persona in TRAINING_PERSONAS}
    assert run["mixed"]["focus_held_out"]["paired_seeds"] == [31, 37]
    specialist_regrets = [
        run["specialists"][persona.id]["mean_regret"] for persona in TRAINING_PERSONAS
    ]
    mixed_regrets = [run["mixed"][persona.id]["mean_regret"] for persona in TRAINING_PERSONAS]
    assert sum(mixed_regrets) > sum(specialist_regrets)
