import json
import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

PROFILE_PATH = os.getenv("PROFILE_PATH", "../data/profile.json")

def load_profile() -> Dict[str, Any]:
    if not os.path.exists(PROFILE_PATH):
        return {}
    with open(PROFILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

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
    # Returns a summary of the profile structure without all the raw lists 
    # to avoid context limits, though for this MVP we can return the whole thing.
    return load_profile()
