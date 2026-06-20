import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT_LOG_PATH = os.path.join(BASE_DIR, "data", "audit.log")

def register_audit_log(user_id: str, action: str, amount: float):
    os.makedirs(os.path.dirname(AUDIT_LOG_PATH), exist_ok=True)
    
    log_entry = {
        "user": user_id,
        "action": action,
        "amount": amount,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")