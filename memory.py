
from agent import InterviewAgent
from interviewquestions import QUESTIONS
 
teamwork, leadership = QUESTIONS[0], QUESTIONS[1]
 
weak = "Um, I don't know, basically I just like did some stuff."
strong = ("When I was at my last company, a teammate and I had a conflict. My goal was to resolve it "
          "before the deadline. I listened, communicated my view, and we reached a compromise. "
          "As a result the outcome was good and I learned a lot.")
 
agent = InterviewAgent()
agent.evaluate_answer(leadership, weak)    # weak answer FIRST
agent.evaluate_answer(teamwork, strong)    # strong answer LAST
 
reply = agent.ask_agent("What is my weakest area?")
print(reply)
 
weakest = agent.get_summary()["weakest"]["category"]
if weakest == "Leadership" and "leadership" in reply.lower():
    print("\nPASS: weakest area is Leadership (not the last question).")
else:
    print("\nFAIL: only looking at the last turn.")
 
