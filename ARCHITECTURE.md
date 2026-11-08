# ProcessForge architecture

## Pipeline

1. **Intake** — normalization of unstructured input.
2. **Classification** — deterministic category/priority baseline.
3. **Extraction** — structured fields: email, dates, amounts, document numbers.
4. **Risk guard** — detects sensitive or high-impact cases.
5. **Routing** — maps the case to a business owner.
6. **LLM enrichment** — optional OpenAI-compatible reasoning layer.
7. **Human gate** — requires approval for risky, critical or low-confidence cases.
8. **Audit trail** — every stage is recorded in the response.

## Why hybrid instead of LLM-only

The deterministic baseline keeps the system usable when an LLM is unavailable, makes core routing testable, and reduces uncontrolled actions. The LLM augments rather than replaces the safety-critical path.

## Production extension points

- RAG over approved corporate knowledge;
- adapters for CRM / Service Desk / ERP;
- role-based authorization;
- PII redaction before model calls;
- observability and SLA metrics;
- idempotent action execution;
- policy engine per business process.

## Evaluation targets

For a hackathon brief, measure at least:
- routing accuracy;
- extraction precision/recall;
- share of cases safely automated;
- median processing time;
- false-negative rate of the human-approval guard.
