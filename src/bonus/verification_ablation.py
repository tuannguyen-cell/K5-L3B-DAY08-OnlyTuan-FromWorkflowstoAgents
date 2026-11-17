"""R2 ablation: turn off only the reference swarm's untrusted-delay override.

No reference file or evaluator is edited. The scoped patch prevents the parsed
ticket number from replacing the order's delay; all model calls remain intact.
Run from src: python -m bonus.verification_ablation
"""

import json
from pathlib import Path
from unittest.mock import patch

from lab8.benchmark import run_benchmark
from lab8.config_loader import repo_path
from lab8.db import load_json, load_jsonl


def main():
    world = load_json(repo_path("data", "public_world_state.json"))
    claims = load_jsonl(repo_path("data", "public_claims.jsonl"))
    settings = dict(world=world, claims=claims, shapes=["swarm"], seeds=[11, 22, 33, 44, 55])
    baseline = run_benchmark(**settings)
    # complete(... purpose='parse') still runs with exactly the original prompt.
    # This switch only disables accepting the separate parsed ticket as evidence.
    with patch("lab8.shapes.swarm_reference.parse_delay_days", return_value=None):
        verified = run_benchmark(**settings)
    report = {
        "experiment": "R2-ticket-delay-override",
        "variable": "accept_ticket_delay_override",
        "source": "https://arxiv.org/abs/2503.13657",
        "baseline": baseline,
        "verified": verified,
    }
    path = Path("reports/ablation_ticket_verification.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for arm, result in (("baseline", baseline), ("verified", verified)):
        stats = result["by_shape"]["swarm"]
        print(f"{arm}: pass_rate={stats['pass_rate']:.6f}; cost/success={stats['cost_per_success_vnd']:.6f}")
    print(path)


if __name__ == "__main__":
    main()
