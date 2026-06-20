# test_tools.py
from mcp.agent_tools import (
    get_customer_profile_tool, 
    get_card_limit_tool, 
    update_card_limit_tool, 
    create_pix_tool
)
from mcp.database.mock_db import CLIENTES_DB

def run_tests():
    print("--- Testando Tools do Banco ---")
    
    print("\n1. Consultando Perfil do João (ID 123):")
    # Para chamar a função subjacente de uma @tool do LangChain, usamos .invoke()
    print(get_customer_profile_tool.invoke({"customer_id": "123"}))
    
    print("\n2. Consultando Limite:")
    print(get_card_limit_tool.invoke({"customer_id": "123"}))
    
    print("\n3. Atualizando Limite para R$ 15.000:")
    print(update_card_limit_tool.invoke({"customer_id": "123", "new_limit": 15000.0}))
    
    print("\n4. Confirmando Novo Limite:")
    print(get_card_limit_tool.invoke({"customer_id": "123"}))
    
    print("\n5. Testando PIX com sucesso (R$ 5.000):")
    print(create_pix_tool.invoke({
        "customer_id": "123", 
        "amount": 5000.0, 
        "destination_key": "telefone-joao"
    }))
    
    print("\n6. Testando PIX sem saldo (R$ 30.000):")
    print(create_pix_tool.invoke({
        "customer_id": "123", 
        "amount": 30000.0, 
        "destination_key": "chave-aleatoria"
    }))

if __name__ == "__main__":
    run_tests()