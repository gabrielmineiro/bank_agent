from shared.logger import get_logger, base_extra_args
from shared.audit import register_audit_log

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
        client = self.db.get(customer_id)
        if not client:
            logger.warning("Cliente não encontrado ao consultar limite", extra={"extra": extra_args(customer_id, "get_limit")})
            return "Cliente não encontrado."
            
        logger.info("Limite consultado com sucesso", extra={"extra": extra_args(customer_id, "get_limit", {"limite_cartao": client['limite_cartao']})})
        return f"O limite atual do cartão é R$ {client['limite_cartao']:.2f}"

    def update_limit(self, customer_id: str, new_limit: float) -> str:
        """Atualiza o limite do cartão de crédito do client."""
        logger.info("Solicitação de atualização de limite", extra={"extra": extra_args(customer_id, "update_limit", {"new_limit": new_limit})})
        client = self.db.get(customer_id)
        if not client:
            logger.warning("Cliente não encontrado ao atualizar limite", extra={"extra": extra_args(customer_id, "update_limit")})
            return "Falha: Cliente não encontrado."
        
        old_limit = client["limite_cartao"]
        client["limite_cartao"] = new_limit
        logger.info("Limite atualizado com sucesso", extra={"extra": extra_args(customer_id, "update_limit", {"old_limit": old_limit, "new_limit": new_limit})})
        
        # Registra a alteração de limite na trilha de auditoria
        register_audit_log(user_id=customer_id, action="update_limit", amount=new_limit)
        
        return f"Sucesso: Limite atualizado para R$ {new_limit:.2f}."