import json
import os
 
from dotenv import load_dotenv
from openai import OpenAI
 
from tools import TOOL_SPECS, check_star_structure, detect_filler_words, score_relevance
 
load_dotenv()
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")
MODEL = "openai/gpt-oss-120b"
 
 
def run_tool(name, question, answer):
    """Run one tool. We always use the real answer and keywords from the question."""
    if name == "detect_filler_words":
        return detect_filler_words(answer)
    if name == "check_star_structure":
        return check_star_structure(answer)
    if name == "score_relevance":
        return score_relevance(answer, question["keywords"])
    return {"error": "unknown tool"}
 
 
class InterviewAgent:
    def __init__(self):
        self.results = []   # MEMORY: one dict per answered question
 
    # ---------- Ask 1: evaluate one answer with tools ----------
    def evaluate_answer(self, question, answer):
        messages = [
            {"role": "system", "content":
                "You are a friendly interview coach. Call detect_filler_words and score_relevance "
                "for every answer. Call check_star_structure only for behavioral questions. "
                "Then give feedback in at most 4 short, encouraging sentences."},
            {"role": "user", "content":
                f"Question: {question['question']}\nBehavioral: {question['behavioral']}\n"
                f"Answer: {answer}"},
        ]
        tool_results = {}
        feedback = ""
        for _ in range(4):  # let the AI call tools for a few rounds
            reply = client.chat.completions.create(
                model=MODEL, messages=messages, tools=TOOL_SPECS).choices[0].message
            if not reply.tool_calls:      # no more tools wanted -> this is the feedback
                feedback = reply.content
                break
            messages.append(reply)
            for call in reply.tool_calls:
                result = run_tool(call.function.name, question, answer)
                tool_results[call.function.name] = result
                messages.append({"role": "tool", "tool_call_id": call.id,
                                 "content": json.dumps(result)})
 
        # Make sure we always have the numbers memory needs
        if "score_relevance" not in tool_results:
            tool_results["score_relevance"] = run_tool("score_relevance", question, answer)
        if "detect_filler_words" not in tool_results:
            tool_results["detect_filler_words"] = run_tool("detect_filler_words", question, answer)
 
        star = tool_results.get("check_star_structure")
        record = {
            "category": question["category"],
            "question": question["question"],
            "relevance": tool_results["score_relevance"]["score"],
            "missing": tool_results["score_relevance"]["missing"],
            "fillers": tool_results["detect_filler_words"]["filler_count"],
            "star": star["score"] if star else None,
            "feedback": feedback,
        }
        self.results.append(record)     # remember it
        return record
 
    # ---------- Ask 2: aggregation over ALL answers ----------
    def get_summary(self):
        total = 0
        weakest = self.results[0]
        for r in self.results:
            total += r["relevance"]
            if r["relevance"] < weakest["relevance"]:   # lowest score wins
                weakest = r
        return {"count": len(self.results),
                "average": round(total / len(self.results), 1),
                "weakest": weakest}
 
    def summary_text(self):
        s = self.get_summary()
        lines = [f"Answers so far: {s['count']}",
                 f"Average relevance: {s['average']}/100",
                 f"WEAKEST AREA: {s['weakest']['category']} - {s['weakest']['question']} "
                 f"(score {s['weakest']['relevance']})", "", "All answers:"]
        for r in self.results:
            lines.append(f"- {r['category']}: relevance {r['relevance']}, "
                         f"fillers {r['fillers']}, STAR {r['star']}")
        return "\n".join(lines)
 
    def generate_final_report(self):
        if not self.results:
            return "No answers yet."
        s = self.get_summary()
        w = s["weakest"]
        text = "# Final Report\n\n"
        text += f"- Questions answered: {s['count']}\n"
        text += f"- Average relevance: {s['average']}/100\n"
        text += f"- Weakest area: **{w['category']}** ({w['relevance']}/100)\n"
        text += f"- Try to mention: {', '.join(w['missing'])}\n\n## Scores\n"
        for r in self.results:
            text += f"- {r['category']}: {r['relevance']}/100\n"
        return text
 
    # ---------- Ask 2: meta-questions at any time ----------
    def ask_agent(self, user_question):
        if not self.results:
            return "You haven't answered anything yet."
        reply = client.chat.completions.create(model=MODEL, messages=[
            {"role": "system", "content":
                "You are an interview coach. Answer using ONLY the session data. "
                "The numbers are already computed - do not recalculate. "
                "Name the categories and scores. Keep it short."},
            {"role": "user", "content":
                f"SESSION DATA:\n{self.summary_text()}\n\nQuestion: {user_question}"},
        ]).choices[0].message.content
        return reply
 
