from agent import InterviewAgent
from interviewquestions import QUESTIONS
 
agent = InterviewAgent()
for q in QUESTIONS:
    print("\n" + q["question"])
    answer = input("Your answer: ")
    result = agent.evaluate_answer(q, answer)
    print("Feedback:", result["feedback"])
    print("Relevance:", result["relevance"])
 
print("\n" + agent.ask_agent("How am I doing so far?"))
print("\n" + agent.generate_final_report())
 
