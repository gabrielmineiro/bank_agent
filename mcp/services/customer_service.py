import json
from mcp.database.mock_db import CLIENTES_DB
from shared.logger import get_logger, base_extra_args

logger = get_logger(__name__)

def extra_args(customer_id, extra_fields=None):
    extra_fields = extra_fields or {}
    return base_extra_args(customer_id, "get_profile", extra_fields)

class CustomerService:
    def __init__(self, db):
        self.db = db

    def get_profile(self, customer_id: str) -> str:
        """Consulta o perfil de um cliente no sistema do banco."""
        logger.info("Buscando perfil de cliente", extra={"extra": extra_args(customer_id)})
        cliente = self.db.get(customer_id)
        if not cliente:
            logger.warning("Cliente não encontrado", extra={"extra": extra_args(customer_id)})
            return json.dumps({"erro": "Cliente não encontrado."})
        
        logger.info("Perfil de cliente retornado", extra={"extra": extra_args(customer_id)})
        return json.dumps({
            "customer_id": customer_id,
            "segment": cliente["segmento"],
            "credit_score": cliente["credit_score"]
        })