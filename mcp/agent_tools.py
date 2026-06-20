from langchain_core.tools import StructuredTool

from mcp.services import CustomerService, CardService, TransferService
from mcp.database.mock_db import CLIENTES_DB

customer_svc = CustomerService(CLIENTES_DB)
card_svc = CardService(CLIENTES_DB)
transfer_svc = TransferService(CLIENTES_DB)

get_customer_profile_tool = StructuredTool.from_function(
    func=customer_svc.get_profile,
    name="get_customer_profile",
    description="Consulta o perfil de um cliente no sistema do banco. Usar para checar segmento e score."
)

get_card_limit_tool = StructuredTool.from_function(
    func=card_svc.get_limit,
    name="get_card_limit",
    description="Consulta o limite atual do cartão de crédito do cliente."
)

update_card_limit_tool = StructuredTool.from_function(
    func=card_svc.update_limit,
    name="update_card_limit",
    description="Atualiza o limite do cartão de crédito do cliente. Exige validação prévia."
)

create_pix_tool = StructuredTool.from_function(
    func=transfer_svc.create_pix,
    name="create_pix",
    description="Executa uma transferência PIX da conta do cliente para uma chave destino."
)

TOOLS_BANCARIAS = [
    get_customer_profile_tool,
    get_card_limit_tool,
    update_card_limit_tool,
    create_pix_tool
]