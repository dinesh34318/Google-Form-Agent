import json
from models import FormQuestion
from agent import decide_answers

def run_test():
    questions = [
        FormQuestion(id="q1", question="Full Name", type="short_answer", required=True, options=None),
        FormQuestion(id="q2", question="Registeration number", type="short_answer", required=True, options=None),
        FormQuestion(id="q3", question="Gender", type="multiple_choice", required=True, options=["Male", "Female", "Other", "Prefer not to say"]),
        FormQuestion(id="q4", question="Date of Birth", type="date", required=True, options=None),
        FormQuestion(id="q5", question="Current Year of Study", type="dropdown", required=True, options=["1st Year", "2nd Year", "3rd Year", "4th Year", "Graduate Student", "PhD Candidate", "Faculty/Staff"]),
        FormQuestion(id="q6", question="Unknown AI Field", type="short_answer", required=False, options=None)
    ]
    
    results = decide_answers(questions)
    
    for r in results:
        print(f"Question: {r.question}")
        print(f" -> Field: {r.profile_field}")
        print(f" -> Answer: {r.answer}")
        print(f" -> Needs Input: {r.needs_user_input}")
        print(f" -> Reason: {r.reason}")
        print("-" * 40)

if __name__ == "__main__":
    run_test()
