import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
import os
from models import FormQuestion, AnswerDecision
from profile import load_profile

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# LEVEL 1: Deterministic mappings
DETERMINISTIC_MAP = {
    "full name": "personal.full_name",
    "name": "personal.full_name",
    "student name": "personal.full_name",
    "enter your full name": "personal.full_name",
    "please provide your complete name": "personal.full_name",
    "registeration number": "personal.registration_number",
    "registration number": "personal.registration_number",
    "registration no": "personal.registration_number",
    "student id": "personal.registration_number",
    "student registration id": "personal.registration_number",
    "gender": "personal.gender",
    "date of birth": "personal.date_of_birth",
    "dob": "personal.date_of_birth",
    "birth date": "personal.date_of_birth",
    "current year": "education.current_year",
    "current year of study": "education.current_year",
    "academic year": "education.current_year",
    "which year are you studying?": "education.current_year",
    "which academic year are you currently studying?": "education.current_year"
}

def resolve_field(profile_data: Dict[str, Any], field_path: str) -> Optional[Any]:
    parts = field_path.split('.')
    curr = profile_data
    for p in parts:
        if isinstance(curr, dict) and p in curr:
            curr = curr[p]
        else:
            return None
    return curr if curr != "" else None

async def decide_answers(questions: List[FormQuestion]) -> List[AnswerDecision]:
    profile_data = load_profile()
    decisions = []
    
    # Send only necessary profile sections to AI for privacy
    safe_profile = {
        "personal": profile_data.get("personal", {}),
        "education": profile_data.get("education", {}),
        "skills": profile_data.get("skills", []),
        "projects": profile_data.get("projects", []),
        "experience": profile_data.get("experience", []),
        "preferences": profile_data.get("preferences", {})
    }

    for q in questions:
        q_lower = q.question.lower().strip()
        
        # LEVEL 1: Deterministic
        mapped_field = DETERMINISTIC_MAP.get(q_lower)
        if mapped_field:
            answer = resolve_field(profile_data, mapped_field)
            if answer:
                # Basic option matching for deterministic fields like gender
                if q.options and isinstance(answer, str):
                    for opt in q.options:
                        if answer.lower() == opt.lower():
                            answer = opt
                            break
                            
                decisions.append(AnswerDecision(
                    question=q.question,
                    profile_field=mapped_field,
                    answer=answer,
                    confidence=1.0,
                    fill=True,
                    reason="Deterministic exact match."
                ))
                continue
                
        # LEVEL 2: AI Matching
        try:
            prompt = f"""
You are an AI assistant helping to map a Google Form question to a user's profile.
User Profile: {json.dumps(safe_profile)}

Question to answer: "{q.question}"
Question type: {q.type}
Available options (if any): {q.options}

Instructions:
1. Try to find a matching field in the profile.
2. If there is NO reliable match, set fill=false and answer=null.
3. NEVER guess personal information.
4. If options are provided, your answer MUST match one of the options.
5. Return JSON matching AnswerDecision structure.
"""
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_schema", "json_schema": {
                    "name": "answer_decision",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "profile_field": {"type": ["string", "null"]},
                            "answer": {"type": ["string", "null"]},
                            "confidence": {"type": "number"},
                            "fill": {"type": "boolean"},
                            "reason": {"type": "string"}
                        },
                        "required": ["profile_field", "answer", "confidence", "fill", "reason"],
                        "additionalProperties": False
                    }
                }},
                temperature=0.0
            )
            
            ai_data = json.loads(response.choices[0].message.content)
            
            # LEVEL 3: Unknown / Low confidence validation
            if not ai_data.get("fill") or ai_data.get("confidence", 0) < 0.8 or not ai_data.get("answer"):
                ai_data["fill"] = False
                ai_data["answer"] = None
                
            decisions.append(AnswerDecision(
                question=q.question,
                profile_field=ai_data.get("profile_field"),
                answer=ai_data.get("answer"),
                confidence=ai_data.get("confidence", 0.0),
                fill=ai_data.get("fill", False),
                reason=ai_data.get("reason", "AI mapped.")
            ))
            
        except Exception as e:
            print(f"DEBUG: AI Error: {e}")
            decisions.append(AnswerDecision(
                question=q.question,
                profile_field=None,
                answer=None,
                confidence=0.0,
                fill=False,
                reason=f"Error generating answer: {str(e)}"
            ))
            
    return decisions
