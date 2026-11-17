"""Shape A — deterministic workflow. Student work.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Suggested steps. Money stays in code (`lab8.tools.compute_compensation`).

1. Open the store. Read the claim through `get_claim_view` (not SELECT *).
2. Missing order_id -> status `needs_info`. Do not write the ledger.
3. `lookup_order`. If not visible -> `escalated`. Do not copy phone, address, item, internal note.
4. Quote from the order row. Ignore delay numbers written in the ticket.
5. Quote amount 0 -> `denied`. Do not call issue_refund.
6. Quote amount > 0 -> `durability.issue_refund(conn, claim_id, <full quote>)`.
   Pass the FULL quote. The host checks the claim's own approval and subtracts
   what earlier claims already got for the same order (T13, T14). Do not
   subtract it yourself or the host subtracts twice.
   Auth failure or order already refunded -> `denied` (the host writes `policy_denied`).
   `proposal_amount` stays the full quote. Amount conflict -> `failed`.
7. Success -> `resolved`. One ledger row, one `refund_committed` audit.
8. Use MockLLM only to draft the reply text, if you want a model call at all.

The model must not choose the refund amount and must not commit the refund.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.mock_llm import complete
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id("workflow", claim_id, seed))
    conn = connect(store_path)
    try:
        def done(status, proposal=0, reason=None):
            # Draft only from code's decision. Never send or log raw ticket text.
            complete(budget, seed=seed, purpose="draft", prompt=f"status={status};proposal={proposal}")
            trace.add("decision", {"status": status, "proposal_amount": proposal})
            return finish(conn, shape="workflow", claim_id=claim_id, seed=seed,
                          status=status, proposal_amount=proposal, budget=budget,
                          trace=trace, error_reason=reason)

        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        trace.add("claim", {"found": claim["found"], "has_order": bool(claim.get("order_id"))})
        if not claim["found"]:
            return done("failed", reason="unknown_claim")
        if not claim.get("order_id"):
            return done("needs_info", reason="missing_order_id")
        budget.add_tool(tool_cost())
        view = lookup_order(conn, claim["order_id"], claim["principal_id"])
        trace.add("order_scope", {"visible": view["visible"]})
        if not view["visible"]:
            return done("escalated", reason=view["reason"])
        budget.add_tool(tool_cost())
        quote = compute_compensation(conn, view["order"])
        trace.add("quote", quote)
        proposal = int(quote["amount_vnd"])
        if proposal <= 0:
            return done("denied", reason=quote["reason"])
        # Host owns approval, order cap, ledger transaction, and crash injection.
        trace.add("host_request", {"proposal_amount": proposal})
        trace.write()
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        trace.add("host_result", {"ok": outcome["ok"], "reason": outcome["reason"]})
        status = "resolved" if outcome["ok"] else ("failed" if outcome["conflict"] else "denied")
        return done(status, proposal, None if outcome["ok"] else outcome["reason"])
    finally:
        conn.close()
