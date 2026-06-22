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



BASE_TOOLS = [
    {
        "func": _get_account_balance,
        "name": "get_account_balance",
        "description": (
            "Consulta o saldo atual da conta corrente de um cliente no sistema bancário. "
            "USE ESTA FERRAMENTA quando o usuário perguntar: 'qual meu saldo?', "
            "'quanto tenho na conta?', 'qual o saldo disponível?'. "
            "Requer o customer_id do cliente."
        ),
        "auth": True,
    },
    {
        "func": _get_card_limit,
        "name": "get_card_limit",
        "description": (
            "Consulta o limite atual do cartão de crédito de um cliente. "
            "USE ESTA FERRAMENTA quando o usuário perguntar: 'qual meu limite?', "
            "'quanto de limite eu tenho?', 'limite do cartão'. "
            "Requer o customer_id do cliente."
        ),
        "auth": True,
    },
    {
        "func": _create_pix,
        "name": "create_pix",
        "description": (
            "Executa uma transferência PIX da conta do cliente para uma chave destino. "
            "USE ESTA FERRAMENTA quando o usuário quiser: 'fazer um PIX', "
            "'transferir dinheiro', 'enviar valor para alguém'. "
            "Requer customer_id, amount (valor) e destination_key (chave PIX destino)."
        ),
        "auth": True,
    },
    {
        "func": _search_knowledge_base,
        "name": "search_knowledge_base",
        "description": (
            "OBRIGATÓRIO: Consulta a base de conhecimento oficial do banco. "
            "Você DEVE usar esta ferramenta SEMPRE que o usuário perguntar sobre: "
            "taxas de juros, empréstimos, empréstimo consignado, crédito pessoal, "
            "financiamento, tarifas, regulamentos, regras do banco, seguros, "
            "investimentos, previdência, consórcio, capitalização, aposentados, "
            "ou QUALQUER dúvida sobre produtos, serviços e políticas do banco. "
            "NUNCA responda essas perguntas de memória — sempre consulte esta ferramenta primeiro. "
            "Passe a pergunta completa do usuário como query."
        ),
        "auth": False,
    },
]

