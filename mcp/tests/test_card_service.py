import unittest

from mcp.services.card_service import CardService

class TestCardService(unittest.TestCase):
    def setUp(self):
        self.mock_db = {
            "222": {
                "limite_cartao": 1000.00
            }
        }
        self.service = CardService(self.mock_db)

    def test_get_limit_success(self):
        result = self.service.get_limit("222")
        self.assertIn("R$ 1000.00", result)

    def test_get_limit_not_found(self):
        result = self.service.get_limit("999")
        self.assertEqual(result, "Cliente não encontrado.")

    def test_update_limit_success(self):
        result = self.service.update_limit("222", 5000.00)
        self.assertIn("Sucesso: Limite atualizado", result)
        self.assertEqual(self.mock_db["222"]["limite_cartao"], 5000.00)

    def test_update_limit_not_found(self):
        result = self.service.update_limit("999", 5000.00)
        self.assertEqual(result, "Falha: Cliente não encontrado.")

if __name__ == '__main__':
    unittest.main()
