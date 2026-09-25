import gradio as gr
 
from agent import InterviewAgent
from interviewquestions import QUESTIONS
 
agent = InterviewAgent()   # simple: one agent for the whole demo
position = 0               # which question we are on
 
 
def current_question():
    if position >= len(QUESTIONS):
        return "All questions done! Click 'Get final report'."
    return f"Question {position + 1}/{len(QUESTIONS)}: {QUESTIONS[position]['question']}"
 
 
def scorecard():
    return [[r["category"], r["relevance"], r["fillers"], r["star"]] for r in agent.results]
 
 
def submit(answer):
    global position
    if position >= len(QUESTIONS) or answer.strip() == "":
        return "Please type an answer.", scorecard(), current_question(), answer
    result = agent.evaluate_answer(QUESTIONS[position], answer)
    position += 1
    return result["feedback"], scorecard(), current_question(), ""
 
 
def ask(text):
    return agent.ask_agent(text)
 
 
def report():
    return agent.generate_final_report()
 
 
with gr.Blocks(title="InterviewIQ") as demo:
    gr.Markdown("# InterviewIQ - Mock Interview Coach")
    question_box = gr.Markdown(current_question())
    answer_box = gr.Textbox(label="Your answer", lines=4)
    submit_btn = gr.Button("Submit answer")
    feedback_box = gr.Textbox(label="Feedback", lines=4)
    table = gr.Dataframe(headers=["Category", "Relevance", "Fillers", "STAR"], label="Scorecard")
 
    meta_box = gr.Textbox(label="Ask the coach (e.g. What's my weakest area?)")
    meta_btn = gr.Button("Ask")
    meta_out = gr.Textbox(label="Coach says")
 
    report_btn = gr.Button("Get final report")
    report_out = gr.Markdown()
 
    submit_btn.click(submit, answer_box, [feedback_box, table, question_box, answer_box])
    meta_btn.click(ask, meta_box, meta_out)
    report_btn.click(report, None, report_out)
 
demo.launch()
 
