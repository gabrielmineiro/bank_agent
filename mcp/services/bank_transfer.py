import json
import uuid
from datetime import datetime

from shared.logger import get_logger, base_extra_args
from shared.audit import register_audit_log

logger = get_logger(__name__)

def extra_args(customer_id, amount, destination_key, extra_fields=None):
    extra_fields = extra_fields or {}
    return base_extra_args(customer_id, "create_pix", {"amount": amount, "destination_key": destination_key, **extra_fields})

class TransferService:
    def __init__(self, db):
        self.db = db

    def create_pix(self, customer_id: str, amount: float, destination_key: str) -> str:
        """Executa uma transferência PIX."""
        logger.info("Iniciando transferência PIX", extra={"extra": extra_args(customer_id, amount, destination_key)})
        client = self.db.get(customer_id)
        if not client:
            logger.warning("Cliente não encontrado para PIX", extra={"extra": extra_args(customer_id, amount, destination_key)})
            return json.dumps({"status": "error", "message": "Falha: Cliente não encontrado."})
        
        if client["saldo_conta"] < amount:
            logger.warning("Saldo insuficiente para PIX", extra={"extra": extra_args(customer_id, amount, destination_key, {"saldo_conta": client["saldo_conta"]})})
            return json.dumps({"status": "error", "message": f"Falha: Saldo insuficiente. Saldo é R$ {client['saldo_conta']:.2f}."})
        

        confirm = input("   Confirmar PIX? [sim/não]: ").strip().lower()
        if confirm not in ("sim", "s", "yes"):
            return json.dumps({"status": "error", "message": "Transferência cancelada pelo usuário."})
        
        
        client["saldo_conta"] -= amount
        transaction_id = str(uuid.uuid4())
        logger.info("Transferência PIX realizada com sucesso", extra={"extra": extra_args(customer_id, amount, destination_key, {"transaction_id": transaction_id, "new_balance": client["saldo_conta"]})})
        
        register_audit_log(user_id=customer_id, action="create_pix", amount=amount)
        
        return json.dumps({
            "status": "success",
            "message": "Transferência PIX realizada com sucesso.",
            "data": {
                "transaction_id": transaction_id,
                "amount": amount,
                "destination": destination_key,
                "timestamp": datetime.now().isoformat(),
                "new_balance": client["saldo_conta"]
            }
        })