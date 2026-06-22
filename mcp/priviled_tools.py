
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
            "Consulta o perfil completo de um cliente no sistema do banco (segmento e credit score). "
            "USE ESTA FERRAMENTA quando precisar: 'ver perfil do cliente', "
            "'checar segmento', 'verificar score de crédito'. "
            "Requer o customer_id. Disponível apenas para managers e admins."
        ),
        "auth": False,
    },
    {
        "func": _update_card_limit,
        "name": "update_card_limit",
        "description": (
            "Atualiza o limite do cartão de crédito de um cliente. "
            "USE ESTA FERRAMENTA quando solicitarem: 'alterar limite', "
            "'aumentar limite do cartão', 'reduzir limite'. "
            "Requer customer_id e new_limit. Disponível apenas para managers e admins."
        ),
        "auth": False,
    },
]
