# TypeSafe AI API & Primitives Reference

Source of truth: `https://docs.typesafe.ai` (index: `https://docs.typesafe.ai/llms.txt`). Mintlify serves Markdown at
`<page>.md` (for example, `https://docs.typesafe.ai/api.md`, `https://docs.typesafe.ai/primitives.md`).

## 1. Endpoint, Models & Limits

- **Evaluation endpoint:** `POST https://api.typesafe.ai/v1/systemone`
- **Models endpoint:** `GET https://api.typesafe.ai/v1/models`
- **Headers:**
  - `Authorization: Bearer $TYPESAFE_API_KEY`
  - `Content-Type: application/json`
  - `TypeSafe-Danger-Zone-Long-Context: true` — raises per-request and per-question context from `64k / 32k` to `262k / 262k`. Enable only when needed; default context is faster and more accurate.
  - `TypeSafe-Danger-Zone-Images: true` — enables multimodal image `assets` and the `box` primitive (`jev-1.14.0` / `jev-preview` required for `box`).

| Model / Alias | Target Version | Input Cost | Output Cost | Default Context (Request / Question) |
| --- | --- | --- | --- | --- |
| `jev-latest` | `jev-1.13.0` (rolling to `1.14.0`) | $0.042 / Mtok ($42 / Btok) | Free ($0) | 64k / 32k tokens |
| `jev-preview` | `jev-1.14.0` | $0.042 / Mtok ($42 / Btok) | Free ($0) | 64k / 32k tokens |

**Request rules:**
- Body size at most 32 MiB; UTF-8 JSON without BOM; nesting depth at most 64 levels.
- Finite numbers only (`NaN` and `Infinity` return `400`). Send large IDs as strings.
- All questions in a single `questions` map are evaluated **in parallel and independently** against `state`. Question IDs are for caller code only and are never seen by the model.

## 2. The Four Primitives (Question Types)

| Type | When to Use | Request `criteria` Shape | Answer Fields Returned |
| --- | --- | --- | --- |
| `choice` | Pick one option from a mutually exclusive set (up to 255 options). | `map<string, string \| object \| array \| null>` | `choice` (top key), `probabilities` (map summing to 1.0), `confidence` (0 to 1) |
| `score` | Rate `state` along an ordered spectrum (2 to 10 descriptive levels, indexed `0` to `n-1`). | `array<string \| object \| array>` | `score` (probability-weighted mean `0` to `n-1`), `legend`, `probabilities`, `confidence` (0 to 1) |
| `noul` | Evaluate whether a yes/no condition holds (or check multi-label conditions independently). | Optional `{"true": ..., "false": ...}` | `noul` (probability of yes from `0.0` to `1.0`; no separate `confidence` field) |
| `box` | Locate a single target in an image (`jev-preview` / `jev-1.14.0` + `TypeSafe-Danger-Zone-Images: true`). | None (`criteria` omitted) | `box` (`{"top", "bottom", "left", "right"}` in `0.0` to `1.0`), `confidence` (0 to 1) |

### Writing High-Signal Questions

- **Reference nested state with backticks:** Put structured data in `state` and point each question at the exact path,
  such as ``Does `ticket.messages[0].text` request a refund under `refund_policy`?``.
- **Phrase `noul` positively:** High `noul` (`~1.0`) must mean `yes`. For confidence-style gating on a `noul`, compute
  `abs(2 * noul - 1)`.
- **Describe concrete situations in `score` levels:** Write observable criteria for each level rather than bare numbers
  (`["0", "1", "2"]`) or vague adverbs (`"moderately severe"`). Normalize multi-score combinations in code by dividing
  each score by `len(criteria) - 1`.
- **Use contrastive structure for easily confused options:** `instructions` and `criteria` accept JSON objects:
  ```json
  {
    "type": "choice",
    "instructions": {
      "question": "Which team should handle `ticket.message`?",
      "focus": "Classify the primary action requested."
    },
    "criteria": {
      "billing": {
        "what": "Charges, invoices, refunds, or subscriptions",
        "not_for": "Order delivery tracking or password resets",
        "examples": ["I was charged twice", "Refund my duplicate payment"]
      },
      "technical": {
        "what": "API errors, bugs, crashes, or integration failures",
        "not_for": "Invoice disputes or plan upgrades",
        "examples": ["POST /v1/orders returns 500", "Webhook signature fails"]
      },
      "other": "Requests that fit neither billing nor technical"
    }
  }
  ```

## 3. Core Architectural Patterns

1. **Speculative Fan-Out:** Pack all candidate questions (including branch-specific follow-ups) into a single API call.
   Batching 13 questions in one call is ~11.5x cheaper and ~9.6x faster than serial calls. Code simply ignores
   unused branch answers.
2. **Confidence-Gated Routing:** Split behavior into three zones based on `confidence` (or `noul` thresholds):
   - **High confidence:** Act automatically in code.
   - **Medium confidence:** Ask for confirmation or run a lightweight check.
   - **Low confidence:** Escalate to the System Two LLM or a human. Scale thresholds with action blast radius.
3. **Composite Scoring:** Decompose broad evaluations ("rate this PR" or "score lead quality") into atomic `Score` or
   `Noul` dimensions in one request, normalize each to `0..1`, and combine with explicit weights in code.
4. **Two-Stage Cascade (When One Question Depends on Another):** Make a second request only when the first answer is
   required to fetch new data (for example, ranking 180 skills in Request 1, then reading the full text of the top 3 in
   Request 2).

## 4. Client SDK Quick Templates

### Python (`pip install typesafe-sdk` or `uv add typesafe-sdk`)

```python
from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

with TypeSafeClient(model="jev-latest") as client:  # Reads TYPESAFE_API_KEY
    response = client.system_one(
        state={"message": "Our API integration started returning 500 errors 20 minutes ago."},
        questions={
            "department": Choice(
                instructions="Which team should handle `message`?",
                criteria={
                    "billing": "Payment or subscription issues",
                    "technical": "Bugs, outages, or integration errors",
                    "sales": "Pricing or account upgrades",
                },
            ),
            "severity": Score(
                instructions="How severe is the issue in `message`?",
                criteria=[
                    "Cosmetic or informational question",
                    "Degraded feature with a workaround",
                    "Production outage blocking core operations",
                ],
            ),
            "is_urgent": Noul(
                instructions="Does `message` convey immediate time-sensitivity?",
            ),
        },
    )
    dept = response.answers["department"]
    sev = response.answers["severity"]
    urgent = response.answers["is_urgent"].noul
```

### TypeScript / JavaScript (`npm install @typesafe-ai/sdk`)

```typescript
import { choice, noul, score, TypeSafeClient } from "@typesafe-ai/sdk";

const client = new TypeSafeClient({ defaultModel: "jev-latest" }); // Reads TYPESAFE_API_KEY
const response = await client.systemOne({
  state: { message: "Our API integration started returning 500 errors 20 minutes ago." },
  questions: {
    department: choice("Which team should handle `message`?", {
      billing: "Payment or subscription issues",
      technical: "Bugs, outages, or integration errors",
      sales: "Pricing or account upgrades",
    }),
    severity: score("How severe is the issue in `message`?", [
      "Cosmetic or informational question",
      "Degraded feature with a workaround",
      "Production outage blocking core operations",
    ]),
    is_urgent: noul("Does `message` convey immediate time-sensitivity?"),
  },
});
```
