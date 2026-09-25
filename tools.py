
# Three simple tools. Each takes text and returns a dict. No AI inside - just Python.
 
FILLERS = ["um", "uh", "like", "basically", "actually", "literally", "you know"]
 
 
def clean(text):
    """Lowercase, replace punctuation with spaces, add a space at each end."""
    text = text.lower()
    for ch in ".,!?;:\"()":
        text = text.replace(ch, " ")
    return " " + text + " "
 
 
def detect_filler_words(answer):
    text = clean(answer)
    found = {}
    for word in FILLERS:
        count = text.count(" " + word + " ")
        if count > 0:
            found[word] = count
    return {"filler_count": sum(found.values()), "fillers_found": found}
 
 
# Words that hint each STAR part is present
STAR_HINTS = {
    "Situation": ["when i was", "at my", "during", "our team", "project", "last year", "once"],
    "Task": ["my goal", "my task", "my role", "i needed to", "i had to", "responsible", "deadline"],
    "Action": ["i decided", "i talked", "i listened", "i created", "i organized", "i led",
               "i started", "i built", "i asked", "so i"],
    "Result": ["as a result", "result", "in the end", "outcome", "increased", "reduced",
               "improved", "i learned", "delivered"],
}
 
 
def check_star_structure(answer):
    text = answer.lower()
    found, missing = [], []
    for part, hints in STAR_HINTS.items():
        if any(h in text for h in hints):
            found.append(part)
        else:
            missing.append(part)
    return {"found": found, "missing": missing, "score": 25 * len(found)}
 
 
def score_relevance(answer, expected_keywords):
    text = answer.lower()
    matched = [k for k in expected_keywords if k in text]
    missing = [k for k in expected_keywords if k not in text]
    score = round(100 * len(matched) / len(expected_keywords))
    return {"score": score, "matched": matched, "missing": missing}
 
 
# Description of the tools for the AI (so it knows what it can call)
def _tool(name, description, extra=None):
    props = {"answer": {"type": "string"}}
    if extra:
        props.update(extra)
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": props, "required": ["answer"]}}}
 
 
TOOL_SPECS = [
    _tool("detect_filler_words", "Count filler words like um, like, basically."),
    _tool("check_star_structure", "Check a behavioral answer for Situation, Task, Action, Result."),
    _tool("score_relevance", "Score 0-100 how many expected keywords appear in the answer."),
]
 
