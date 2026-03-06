
prompt = ("You are an analyst.  You receive an array of browsing events.  "
        "Each event has an `event_id` (integer) and other metadata.  "
        "Identify all main topics the user is exploring.  Return valid "
        "JSON in the form: [{ 'topic': str, 'description': str, "
        "'event_range': [start_id, end_id] }, ...]  "
        "Order the array by importance / user activity.  "
        "Always cite the smallest contiguous event_id range covering the topic.")

examples = """**Breakdown**

"""

rubric = f"""
You are an impartial judge evaluating answers produced by another LLM.    
Go through each rubric category, assign a score **1–4** (whole numbers only) and give a one‑sentence justification.  
Apply the rubric to entire numbered sections
For sections with multiple bullet points, give comments on each bullet point explaining why it contributes to the score of the section.
Do not evaluate the entire text at once.


## Rubric Categories

### 1. Clarity:
Definition: The meaning of the text is obvious and transparent. There is no missing context to fully understand each part of what is said.
| Score | Description |
|-------|-------------|
| 1 — Failure   | Response is incoherent or impossible to follow; meaning is lost. |
| 2 — Poor      | Frequent ambiguities or convoluted wording impede understanding. |
| 3 — Good      | Generally easy to follow with only minor awkward phrasing. |
| 4 — Exemplary | Crystal‑clear prose; ideas flow logically and require no rereading. |

### 2. Detailed
| Score | Description |
|-------|-------------|
| 1 — Failure   | Omits key information or contains mostly irrelevant filler. |
| 2 — Poor      | Mentions some relevant points but misses several essential details. |
| 3 — Good      | Covers all major points with adequate depth; minor details absent. |
| 4 — Exemplary | Exhaustive yet focused coverage; includes pertinent examples, numbers, or citations where appropriate. |

### 3. Comprehensiveness 
| Score | Description |
|-------|-------------|
| 1 — Failure   | Addresses <50 % of the task requirements. |
| 2 — Poor      | Covers 50‑75 % of requirements or addresses them superficially. |
| 3 — Good      | Addresses ≥ 90 % of requirements with reasonable depth. |
| 4 — Exemplary | Fully satisfies 100 % of task requirements and anticipates edge cases or follow‑ups. |

### 4. Conciseness  
| Score | Description |
|-------|-------------|
| 1 — Failure   | Mostly fluff or repetition; key points buried. |
| 2 — Poor      | Wordy; could be trimmed by >30 % without loss of meaning. |
| 3 — Good      | Minor extraneous wording; overall length appropriate. |
| 4 — Exemplary | Delivers maximum information with minimum words; no redundancy. |

### 5. Accuracy *(factual + logical)*  
| Score | Description |
|-------|-------------|
| 1 — Failure   | Contains major factual errors or contradicts the raw data. |
| 2 — Poor      | One significant error or several minor inaccuracies. |
| 3 — Good      | Factually correct except for ≤ 1 minor oversight. |
| 4 — Exemplary | Flawless alignment with raw data; sound reasoning throughout. |

### 6. Usefulness / Actionability  
| Score | Description |
|-------|-------------|
| 1 — Failure   | Provides no actionable insight or value to an end user. |
| 2 — Poor      | Offers limited utility; user must heavily re‑work it. |
| 3 — Good      | Immediately helpful with minor tweaks. |
| 4 — Exemplary | Directly actionable; adds extra value (e.g., recommendations, next steps). |


---

Example analysis: 
{examples}

---

## How to respond
Return **markdown** exactly in the structure below:

```markdown
<Current LLM Model>
<Section Name> 

**Breakdown**
"<Copy each bullet point in the section one by one>"
    -  <followed by an analysis comment about how it contributes to the section score and category>
    
**Scores**
| Category | Score | Justification |
|----------|-------|---------------|
| Clarity | <1‑4> | <one sentence> |
| Detail | <1‑4> | <one sentence> |
| Comprehensiveness | <1‑4> | <one sentence> |
| Conciseness | <1‑4> | <one sentence> |
| Accuracy | <1‑4> | <one sentence> |
| Usefulness | <1‑4> | <one sentence> |

**Overall Average**: <rounded mean 1‑4>

**Overall Rationale**  
<1‑2 concise sentences summarizing strengths & weaknesses>
"""

def get_rubric():
    return rubric