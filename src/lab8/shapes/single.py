"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id("single", claim_id, seed))
    conn = connect(store_path)
    try:
        def done(status, proposal=0, reason=None):
            complete(budget, seed=seed, purpose="draft", prompt=f"status={status};proposal={proposal}")
            trace.add("decision", {"status": status, "proposal_amount": proposal})
            return finish(conn, shape="single", claim_id=claim_id, seed=seed,
                          status=status, proposal_amount=proposal, budget=budget,
                          trace=trace, error_reason=reason)

        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        trace.add("claim", {"found": claim["found"], "has_order": bool(claim.get("order_id"))})
        if not claim["found"]:
            return done("failed", reason="unknown_claim")
        if not claim.get("order_id"):
            return done("needs_info", reason="missing_order_id")

        def decide(seen):
            # MockLLM has no tool-call API: the adapter maps observation states
            # to permitted read actions. Its generated text never sets money.
            last = seen.get("last_tool")
            complete(budget, seed=seed, purpose="decide", prompt=f"last_tool={last};task=verify_claim")
            if last is None:
                action = {"tool": "lookup_order", "args": {
                    "order_id": claim["order_id"], "principal_id": claim["principal_id"]}}
            elif last == "lookup_order":
                view = seen["last_result"]
                trace.add("order_scope", {"visible": view["visible"]})
                if not view["visible"]:
                    return {"final": {"status": "escalated", "reason": view["reason"]}}
                action = {"tool": "compute_compensation", "args": {"order": view["order"]}}
            else:
                quote = seen["last_result"]
                trace.add("quote", quote)
                return {"final": {"quote": quote}}
            trace.add("read_action", {"tool": action["tool"]})
            return action

        loop = run_react(conn, budget, observation={"claim": claim}, decide=decide,
                         max_steps=8, worker=True)
        final = loop["final"]
        if "quote" not in final:
            return done(final.get("status", "failed"),
                        reason=final.get("reason", final.get("error_reason")))
        quote = final["quote"]
        proposal = int(quote["amount_vnd"])
        if proposal <= 0:
            return done("denied", reason=quote["reason"])
        trace.add("host_request", {"proposal_amount": proposal})
        trace.write()
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        trace.add("host_result", {"ok": outcome["ok"], "reason": outcome["reason"]})
        status = "resolved" if outcome["ok"] else ("failed" if outcome["conflict"] else "denied")
        return done(status, proposal, None if outcome["ok"] else outcome["reason"])
    finally:
        conn.close()
