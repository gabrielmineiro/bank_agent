import json

from shared.logger import get_logger, base_extra_args

logger = get_logger(__name__)

def extra_args(customer_id, action, extra_fields=None):
    extra_fields = extra_fields or {}
    return base_extra_args(customer_id, action, extra_fields)

class CustomerService:
    def __init__(self, db):
        self.db = db

    def get_profile(self, customer_id: str) -> str:
        """Consulta o perfil de um cliente no sistema do banco."""
        logger.info("Buscando perfil de cliente", extra={"extra": extra_args(customer_id, "get_profile")})
        client = self.db.get(customer_id)
        if not client:
            logger.warning("Cliente não encontrado", extra={"extra": extra_args(customer_id, "get_profile")})
            return json.dumps({"erro": "Cliente não encontrado."})
        
        logger.info("Perfil de cliente retornado", extra={"extra": extra_args(customer_id, "get_profile")})
        return json.dumps({
            "customer_id": customer_id,
            "segment": client["segmento"],
            "credit_score": client["credit_score"]
        })

    def get_balance(self, customer_id: str) -> str:
        """Consulta o saldo atual da conta corrente do cliente."""
        logger.info("Buscando saldo da conta", extra={"extra": extra_args(customer_id, "get_balance")})
        client = self.db.get(customer_id)
        if not client:
            logger.warning("Cliente não encontrado", extra={"extra": extra_args(customer_id, "get_balance")})
            return json.dumps({"erro": "Cliente não encontrado."})
        
        logger.info("Saldo da conta retornado", extra={"extra": extra_args(customer_id, "get_balance")})
        return json.dumps({
            "customer_id": customer_id,
            "account_balance": client["saldo_conta"]
        })