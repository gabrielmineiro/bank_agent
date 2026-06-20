import json
import uuid
from datetime import datetime
from mcp.database.mock_db import CLIENTES_DB
from shared.logger import get_logger, base_extra_args

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
        cliente = self.db.get(customer_id)
        if not cliente:
            logger.warning("Cliente não encontrado para PIX", extra={"extra": extra_args(customer_id, amount, destination_key)})
            return "Falha: Cliente não encontrado."
        
        if cliente["saldo_conta"] < amount:
            logger.warning("Saldo insuficiente para PIX", extra={"extra": extra_args(customer_id, amount, destination_key, {"saldo_conta": cliente["saldo_conta"]})})
            return f"Falha: Saldo insuficiente. Saldo é R$ {cliente['saldo_conta']:.2f}."
        
        cliente["saldo_conta"] -= amount
        transaction_id = str(uuid.uuid4())
        logger.info("Transferência PIX realizada com sucesso", extra={"extra": extra_args(customer_id, amount, destination_key, {"transaction_id": transaction_id, "new_balance": cliente["saldo_conta"]})})
        
        return json.dumps({
            "status": "sucesso",
            "transaction_id": transaction_id,
            "amount": amount,
            "destination": destination_key,
            "timestamp": datetime.now().isoformat(),
            "new_balance": cliente["saldo_conta"]
        })