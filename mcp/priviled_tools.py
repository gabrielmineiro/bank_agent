
from mcp.services import CustomerService, CardService
from mcp.database.mock_db import CLIENTS_DB

customer_svc = CustomerService(CLIENTS_DB)
card_svc = CardService(CLIENTS_DB)


def _get_customer_profile(customer_id: str) -> str:
    """Consulta o perfil completo de um cliente (segmento e score)."""
    return customer_svc.get_profile(customer_id)


def _update_card_limit(customer_id: str, new_limit: float) -> str:
    """Atualiza o limite do cartão de crédito de um cliente."""
    return card_svc.update_limit(customer_id, new_limit)

PRIVILEGED_TOOLS = [
    {
        "func": _get_customer_profile,
        "name": "get_customer_profile",
        "description": (
            "Consulta o perfil de um cliente no sistema do banco. "
            "Usar para checar segmento e score. Disponível apenas para managers e admins."
        ),
        "auth": False,
    },
    {
        "func": _update_card_limit,
        "name": "update_card_limit",
        "description": (
            "Atualiza o limite do cartão de crédito do cliente. "
            "Exige validação prévia. Disponível apenas para managers e admins."
        ),
        "auth": False,
    },
]
