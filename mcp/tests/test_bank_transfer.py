import unittest
import json

from mcp.services.bank_transfer import TransferService

class TestTransferService(unittest.TestCase):
    def setUp(self):
        self.mock_db = {
            "333": {
                "saldo_conta": 1000.00
            }
        }
        self.service = TransferService(self.mock_db)

    def test_create_pix_success(self):
        result_json = self.service.create_pix("333", 200.00, "chave-teste")
        result = json.loads(result_json)
        self.assertEqual(result["status"], "sucesso")
        self.assertEqual(result["amount"], 200.00)
        self.assertEqual(result["destination"], "chave-teste")
        self.assertEqual(result["new_balance"], 800.00)
        self.assertEqual(self.mock_db["333"]["saldo_conta"], 800.00)

    def test_create_pix_not_found(self):
        result = self.service.create_pix("999", 200.00, "chave-teste")
        self.assertEqual(result, "Falha: Cliente não encontrado.")

    def test_create_pix_insufficient_funds(self):
        result = self.service.create_pix("333", 2000.00, "chave-teste")
        self.assertIn("Falha: Saldo insuficiente", result)
        self.assertEqual(self.mock_db["333"]["saldo_conta"], 1000.00) # Saldo não deve ter mudado

if __name__ == '__main__':
    unittest.main()
