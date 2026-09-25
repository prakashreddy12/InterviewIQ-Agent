# InterviewIQ — AI Mock-Interview Coach

An AI agent that acts as a mock-interview coach with a working browser interface.
Give it a spoken/typed answer to an interview question and it evaluates the answer
using a set of tools, gives short feedback, remembers the whole session, and can
answer questions about your overall performance at any point — not just at the end.

## What it does

- **Tool-calling evaluator.** The agent reads your answer and calls the tools it needs:
  - `detect_filler_words` — flags filler words ("um", "like", "basically", ...)
  - `check_star_structure` — checks a behavioral answer for Situation, Task, Action, Result
  - `score_relevance` — scores 0–100 how many expected keywords/ideas the answer covers
- **Session memory with real aggregation.** Every answer's scores are kept for the whole
  session. The agent can report an average relevance score and name the **weakest
  question** (the lowest-scoring one, not just the most recent one).
- **Meta-questions any time.** Ask "How am I doing so far?" or "What's my weakest area?"
  mid-session and get an answer based on everything scored so far.
- **Gradio UI.** Question + answer box, feedback panel, a live scorecard of every question
  answered, a box to ask the coach meta-questions, and a button for a final report.

## Tech stack

- Python
- [LLM provider — Groq 
- Gradio (browser UI)
- Rule-based scoring tools (no ML model needed for filler/STAR/relevance — see `tools.py`)

## Project structure

```
InterviewIQ-Agent/
├── agent.py               # Agent: tool-calling loop, memory, aggregation, meta-Q&A
├── app.py                 # Gradio interface
├── main.py                # Command-line runner
├── memory.py               # Test: proves memory looks at the whole session, not just the last turn
├── interviewquestions.py   # Question bank
├── tools.py                # The three rule-based evaluation tools
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:
```
PROVIDER=groq
GROQ_API_KEY=your_key_here
```

## Run it

```bash
python main.py          # command-line version — try one full Q&A turn
python memory.py         # verifies memory: scores one strong + one weak answer,
                          # then checks the agent correctly names the weak one as weakest
python app.py            # Gradio browser app
```

## How memory works

Every evaluated answer is stored as a record (question, category, relevance score,
filler count, STAR score, missing keywords). The **weakest area** is computed by
scanning all records for the lowest relevance score — not by looking at whichever
question was answered most recently. `memory.py` proves this: it deliberately answers
a weak question first and a strong one last, and checks the agent still names the
weak one.

## Known limitations

- The keyword-relevance scoring is exact-match, not semantic — a synonym for an
  expected keyword won't be credited.
