# services/event_store.py
import json
from pathlib import Path
from datetime import datetime

EVENTS_FILE = Path("data/events.json")

def load_events():
    if not EVENTS_FILE.exists():
        return []
    with open(EVENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_event(image_name: str, detection_result: dict):
    events = load_events()

    event = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_name": image_name,
        "objects": detection_result["objects"],
        "summary": detection_result["summary"]
    }

    events.append(event)

    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

    return event

def get_last_event():
    events = load_events()
    return events[-1] if events else None