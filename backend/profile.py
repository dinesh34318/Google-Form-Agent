import json
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "data"))
PROFILE_PATH = os.environ.get("PROFILE_PATH", os.path.join(DATA_DIR, "profile.json"))

def load_profile() -> Dict[str, Any]:
    if not os.path.exists(PROFILE_PATH):
        print(f"DEBUG: Profile not found at {PROFILE_PATH}")
        return {}
    
    try:
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"DEBUG: Profile loaded successfully from {PROFILE_PATH}")
            if "personal" in data:
                for k, v in data["personal"].items():
                    print(f"DEBUG: personal.{k} = {'available' if v else 'missing'}")
            if "education" in data:
                for k, v in data["education"].items():
                    print(f"DEBUG: education.{k} = {'available' if v else 'missing'}")
            return data
    except Exception as e:
        print(f"DEBUG: Error loading profile: {e}")
        return {}

def save_profile(profile_data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    with open(PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

def update_preference(key: str, value: Any) -> None:
    profile = load_profile()
    if "preferences" not in profile:
        profile["preferences"] = {}
    profile["preferences"][key] = value
    save_profile(profile)

def get_profile_summary() -> Dict[str, Any]:
    return load_profile()
