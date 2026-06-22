import unittest
import json

from mcp.services.customer_service import CustomerService


class TestCustomerService(unittest.TestCase):
    def setUp(self):
        self.mock_db = {
            "111": {
                "nome": "Teste",
                "segmento": "Varejo",
                "credit_score": 500,
                "saldo_conta": 1500.00,
            },
            "222": {
                "nome": "Maria",
                "segmento": "Personnalité",
                "credit_score": 820,
                "saldo_conta": 25000.00,
            },
        }
        self.service = CustomerService(self.mock_db)

    # ── get_profile ──────────────────────────────────────────────

    def test_get_profile_success(self):
        result = json.loads(self.service.get_profile("111"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["customer_id"], "111")
        self.assertEqual(result["data"]["segment"], "Varejo")
        self.assertEqual(result["data"]["credit_score"], 500)

    def test_get_profile_not_found(self):
        result = json.loads(self.service.get_profile("999"))
        self.assertEqual(result["status"], "error")
        self.assertIn("não encontrado", result["message"])

    def test_get_profile_returns_valid_json(self):
        """Garante que a resposta é sempre JSON parseável."""
        raw = self.service.get_profile("111")
        self.assertIsInstance(json.loads(raw), dict)

    def test_get_profile_different_clients(self):
        """Verifica que dados não vazam entre clientes."""
        result_111 = json.loads(self.service.get_profile("111"))
        result_222 = json.loads(self.service.get_profile("222"))
        self.assertEqual(result_111["data"]["segment"], "Varejo")
        self.assertEqual(result_222["data"]["segment"], "Personnalité")
        self.assertNotEqual(
            result_111["data"]["credit_score"],
            result_222["data"]["credit_score"],
        )

    # ── get_balance ──────────────────────────────────────────────

    def test_get_balance_success(self):
        result = json.loads(self.service.get_balance("111"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["customer_id"], "111")
        self.assertEqual(result["data"]["account_balance"], 1500.00)

    def test_get_balance_not_found(self):
        result = json.loads(self.service.get_balance("999"))
        self.assertEqual(result["status"], "error")
        self.assertIn("não encontrado", result["message"])

    def test_get_balance_returns_valid_json(self):
        raw = self.service.get_balance("111")
        self.assertIsInstance(json.loads(raw), dict)

    def test_get_balance_different_clients(self):
        result_111 = json.loads(self.service.get_balance("111"))
        result_222 = json.loads(self.service.get_balance("222"))
        self.assertEqual(result_111["data"]["account_balance"], 1500.00)
        self.assertEqual(result_222["data"]["account_balance"], 25000.00)


if __name__ == "__main__":
    unittest.main()
