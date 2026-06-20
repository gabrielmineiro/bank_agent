from mcp.services import CustomerService, CardService, TransferService
from mcp.database.mock_db import CLIENTS_DB
from kb.setup_rag import search
from shared.permissions import require_access

customer_svc = CustomerService(CLIENTS_DB)
card_svc = CardService(CLIENTS_DB)
transfer_svc = TransferService(CLIENTS_DB)



@require_access("você só pode consultar o saldo da sua própria conta.")
def _get_account_balance(role: str, user_id: str, customer_id: str) -> str:
    """Consulta o saldo atual da conta corrente."""
    return customer_svc.get_balance(customer_id)


@require_access("você só pode consultar o limite do seu próprio cartão.")
def _get_card_limit(role: str, user_id: str, customer_id: str) -> str:
    """Consulta o limite atual do cartão de crédito."""
    return card_svc.get_limit(customer_id)


@require_access("você só pode realizar transferências da sua própria conta.")
def _create_pix(role: str, user_id: str, customer_id: str, amount: float, destination_key: str) -> str:
    """Executa uma transferência PIX."""
    return transfer_svc.create_pix(customer_id, amount, destination_key)


def _search_knowledge_base(query: str) -> str:
    """Consulta a base de conhecimento do banco."""
    return search(query)


def _get_customer_profile(customer_id: str) -> str:
    """Consulta o perfil completo de um cliente (segmento e score)."""
    return customer_svc.get_profile(customer_id)


def _update_card_limit(customer_id: str, new_limit: float) -> str:
    """Atualiza o limite do cartão de crédito de um cliente."""
    return card_svc.update_limit(customer_id, new_limit)



BASE_TOOLS = [
    {
        "func": _get_account_balance,
        "name": "get_account_balance",
        "description": (
            "Consulta o saldo atual da conta corrente do cliente. "
            "Use isso quando ele perguntar quanto dinheiro tem na conta."
        ),
        "auth": True,
    },
    {
        "func": _get_card_limit,
        "name": "get_card_limit",
        "description": "Consulta o limite atual do cartão de crédito do cliente.",
        "auth": True,
    },
    {
        "func": _create_pix,
        "name": "create_pix",
        "description": "Executa uma transferência PIX da conta do cliente para uma chave destino.",
        "auth": True,
    },
    {
        "func": _search_knowledge_base,
        "name": "search_knowledge_base",
        "description": (
            "ÚTIL SEMPRE que o usuário fizer perguntas gerais sobre taxas, regras, tarifas, "
            "empréstimos, regulamentos ou dúvidas institucionais do banco. "
            "Passe a dúvida do usuário como query."
        ),
        "auth": False,
    },
]

