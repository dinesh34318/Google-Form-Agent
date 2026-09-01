import urllib.parse
from typing import List
from models import FormQuestion, AnswerDecision

def generate_prefilled_url(form_url: str, questions: List[FormQuestion], answers: List[AnswerDecision]) -> str:
    """
    Generates a native Google Forms pre-filled URL based on the extracted entry IDs.
    """
    if "viewform" in form_url:
        form_url = form_url.split("?")[0]
            
    params = {}
    ans_map = {a.question: a for a in answers}
    
    for q in questions:
        if q.entry_id:
            decision = ans_map.get(q.question)
            if decision and decision.fill and decision.answer:
                params[f"entry.{q.entry_id}"] = str(decision.answer)
                
    if not params:
        return form_url
        
    query_string = urllib.parse.urlencode(params)
    separator = "&" if "?" in form_url else "?"
    return f"{form_url}{separator}{query_string}"
