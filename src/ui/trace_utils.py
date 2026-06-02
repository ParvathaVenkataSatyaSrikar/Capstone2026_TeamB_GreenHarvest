"""Parse stored agent trace fields."""
import json


def escalation_from_row(row: dict) -> str:
    trace = row.get("agent_trace")
    if isinstance(trace, str):
        try:
            trace = json.loads(trace)
        except json.JSONDecodeError:
            trace = {}
    if isinstance(trace, dict):
        esc = trace.get("escalation", {})
        if isinstance(esc, dict):
            reasons = esc.get("reasons", [])
            if reasons:
                return ", ".join(str(r) for r in reasons)
    return ""
