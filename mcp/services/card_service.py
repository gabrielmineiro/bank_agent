from mcp.database.mock_db import CLIENTES_DB
from shared.logger import get_logger, base_extra_args

logger = get_logger(__name__)

def extra_args(customer_id, action, extra_fields=None):
    extra_fields = extra_fields or {}
    return base_extra_args(customer_id, action, extra_fields)

class CardService:
    def __init__(self, db):
        self.db = db

    def get_limit(self, customer_id: str) -> str:
        """Consulta o limite atual do cartão de crédito do cliente."""
        logger.info("Consultando limite do cartão", extra={"extra": extra_args(customer_id, "get_limit")})
        cliente = self.db.get(customer_id)
        if not cliente:
            logger.warning("Cliente não encontrado ao consultar limite", extra={"extra": extra_args(customer_id, "get_limit")})
            return "Cliente não encontrado."
            
        logger.info("Limite consultado com sucesso", extra={"extra": extra_args(customer_id, "get_limit", {"limite_cartao": cliente['limite_cartao']})})
        return f"O limite atual do cartão é R$ {cliente['limite_cartao']:.2f}"

    def update_limit(self, customer_id: str, new_limit: float) -> str:
        """Atualiza o limite do cartão de crédito do cliente."""
        logger.info("Solicitação de atualização de limite", extra={"extra": extra_args(customer_id, "update_limit", {"new_limit": new_limit})})
        cliente = self.db.get(customer_id)
        if not cliente:
            logger.warning("Cliente não encontrado ao atualizar limite", extra={"extra": extra_args(customer_id, "update_limit")})
            return "Falha: Cliente não encontrado."
        
        old_limit = cliente["limite_cartao"]
        cliente["limite_cartao"] = new_limit
        logger.info("Limite atualizado com sucesso", extra={"extra": extra_args(customer_id, "update_limit", {"old_limit": old_limit, "new_limit": new_limit})})
        return f"Sucesso: Limite atualizado para R$ {new_limit:.2f}."