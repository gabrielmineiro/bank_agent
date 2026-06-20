import logging
import json 
from datetime import datetime

class StructuredFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        return json.dumps(log_record)


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(StructuredFormatter())
        logger.addHandler(console_handler)
    return logger

def base_extra_args(customer_id, action, extra_fields):
    return {"customer_id": customer_id, "action":action, "timestamp": datetime.now().isoformat(), **extra_fields}
