import os
import json
from typing import List, Dict, Any, Literal
from openai import OpenAI
from pydantic import BaseModel, Field
from models import FormQuestion, AnswerDecision
from profile import load_profile
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class CategoryResponse(BaseModel):
    category: Literal["personal", "education", "skills", "projects", "experience", "preferences", "none"]

class AgentResponse(BaseModel):
    profile_field: str | None = Field(description="The field path in the profile (e.g. personal.full_name), or null if not found")
    answer: Any | None = Field(description="The actual answer value to use, or null if unknown")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    needs_user_input: bool = Field(description="True if the user needs to provide or confirm this answer")
    reason: str = Field(description="Reasoning for this decision")

DETERMINISTIC_MAP = {
    "full name": "personal.full_name",
    "name": "personal.full_name",
    "complete name": "personal.full_name",
    "student name": "personal.full_name",
    "your name": "personal.full_name",
    "registeration number": "personal.registration_number",
    "registration number": "personal.registration_number",
    "registration no": "personal.registration_number",
    "registration id": "personal.registration_number",
    "student id": "personal.registration_number",
    "gender": "personal.gender",
    "sex": "personal.gender",
    "date of birth": "personal.date_of_birth",
    "dob": "personal.date_of_birth",
    "birth date": "personal.date_of_birth",
    "born on": "personal.date_of_birth",
    "current year": "education.current_year",
    "current year of study": "education.current_year",
    "year of study": "education.current_year",
    "academic year": "education.current_year",
    "study year": "education.current_year",
    "present year of study": "education.current_year",
    "cgpa": "education.cgpa",
    "your current cgpa": "education.cgpa",
    "college": "education.college",
    "branch": "education.branch"
}

def resolve_field_path(profile: dict, path: str):
    keys = path.split('.')
    val = profile
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return None
    return val

def exact_match(question: str, q_type: str, options: list, profile: dict) -> AnswerDecision | None:
    q_clean = question.lower().strip().replace("?", "").replace("*", "")
    
    if q_clean in DETERMINISTIC_MAP:
        field_path = DETERMINISTIC_MAP[q_clean]
        val = resolve_field_path(profile, field_path)
        
        if val is not None and str(val).strip() != "":
            if q_type in ["multiple_choice", "dropdown"] and options:
                # Find exact match in options
                for opt in options:
                    if str(val).lower() == str(opt).lower():
                        return AnswerDecision(
                            question=question,
                            profile_field=field_path,
                            answer=opt,
                            confidence=1.0,
                            needs_user_input=False,
                            reason=f"Deterministic match to {field_path} and option validated"
                        )
                # If it doesn't match perfectly, fallback to AI
                return None
            else:
                return AnswerDecision(
                    question=question,
                    profile_field=field_path,
                    answer=val,
                    confidence=1.0,
                    needs_user_input=False,
                    reason=f"Deterministic match to {field_path}"
                )
    return None

def decide_answers(questions: List[FormQuestion]) -> List[AnswerDecision]:
    profile_data = load_profile()
    decisions = []
    
    # Create an available-only summary for AI to prevent hallucinating
    available_profile = {}
    for cat, data in profile_data.items():
        if isinstance(data, dict):
            available_profile[cat] = {k: "available" for k, v in data.items() if v}
    
    for q in questions:
        # Step 1: Try deterministic exact match
        det_decision = exact_match(q.question, q.type, q.options, profile_data)
        if det_decision:
            print(f"DEBUG: Deterministic match for '{q.question}' -> {det_decision.profile_field}")
            decisions.append(det_decision)
            continue
            
        print(f"DEBUG: Falling back to AI for '{q.question}'")
        user_content = f"Question: {q.question}\nType: {q.type}\nRequired: {q.required}\nOptions: {q.options}"
        
        try:
            # Step 2: Categorize the question using available summary
            cat_prompt = f"""
You are an AI that categorizes form questions to determine which part of a user's profile is needed.
Available categories with data: {list(available_profile.keys())}
If none apply, output 'none'.
            """
            cat_resp = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": cat_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format=CategoryResponse,
            )
            category = cat_resp.choices[0].message.parsed.category
            
            # Step 3: Extract answer using actual relevant data
            relevant_data = profile_data.get(category, {}) if category != "none" else {}
            
            system_prompt = f"""
You are FormAgent, a personal AI assistant that fills Google Forms for the user.
Your job is to match form questions to the provided personal profile data.
You MUST NEVER invent personal information. If the information is not in the data or cannot be confidently derived, set `needs_user_input` to true and `answer` to null.

Here is the relevant portion of the user's personal profile (JSON):
```json
{json.dumps({category: relevant_data}, indent=2)}
```

For multiple_choice, dropdown, and checkbox questions, your answer MUST match one (or more for checkboxes) of the provided options exactly.
If the data contains the answer but it needs to be mapped to an exact option, do so. If there is no matching option, set needs_user_input to true.
            """
            
            response = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format=AgentResponse,
            )
            
            agent_resp = response.choices[0].message.parsed
            
            decision = AnswerDecision(
                question=q.question,
                profile_field=agent_resp.profile_field,
                answer=agent_resp.answer,
                confidence=agent_resp.confidence,
                needs_user_input=agent_resp.needs_user_input,
                reason=agent_resp.reason
            )
            
            # Validation for choices
            if decision.answer is not None and not decision.needs_user_input:
                if q.type in ["multiple_choice", "dropdown"] and q.options:
                    if decision.answer not in q.options:
                        decision.needs_user_input = True
                        decision.reason += " (Answer did not perfectly match available options)"
                elif q.type == "checkbox" and q.options:
                    if isinstance(decision.answer, list):
                        if not all(a in q.options for a in decision.answer):
                            decision.needs_user_input = True
                            decision.reason += " (Some checkbox answers did not match options)"
                    else:
                         if decision.answer not in q.options:
                             decision.needs_user_input = True
                             decision.reason += " (Answer did not perfectly match available options)"
                             
            decisions.append(decision)
            
        except Exception as e:
            print(f"DEBUG: AI Error: {e}")
            decisions.append(AnswerDecision(
                question=q.question,
                profile_field=None,
                answer=None,
                confidence=0.0,
                needs_user_input=True,
                reason=f"Error generating answer: {str(e)}"
            ))
            
    return decisions
