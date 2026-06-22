import unittest
import json
from unittest.mock import patch

from mcp.services.card_service import CardService


class TestCardService(unittest.TestCase):
    def setUp(self):
        self.mock_db = {
            "222": {
                "limite_cartao": 1000.00,
            },
            "333": {
                "limite_cartao": 5000.00,
            },
        }
        self.service = CardService(self.mock_db)

    # ── get_limit ────────────────────────────────────────────────

    def test_get_limit_success(self):
        result = json.loads(self.service.get_limit("222"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["limite_cartao"], 1000.00)
        self.assertIn("R$ 1000.00", result["message"])

    def test_get_limit_not_found(self):
        result = json.loads(self.service.get_limit("999"))
        self.assertEqual(result["status"], "error")
        self.assertIn("não encontrado", result["message"])

    def test_get_limit_returns_valid_json(self):
        raw = self.service.get_limit("222")
        self.assertIsInstance(json.loads(raw), dict)

    def test_get_limit_different_clients(self):
        result_222 = json.loads(self.service.get_limit("222"))
        result_333 = json.loads(self.service.get_limit("333"))
        self.assertEqual(result_222["data"]["limite_cartao"], 1000.00)
        self.assertEqual(result_333["data"]["limite_cartao"], 5000.00)

    # ── update_limit ─────────────────────────────────────────────

    @patch("builtins.input", return_value="sim")
    def test_update_limit_success(self, _mock_input):
        result = json.loads(self.service.update_limit("222", 5000.00))
        self.assertEqual(result["status"], "success")
        self.assertIn("5000.00", result["message"])
        self.assertEqual(result["data"]["new_limit"], 5000.00)
        self.assertEqual(self.mock_db["222"]["limite_cartao"], 5000.00)

    def test_update_limit_not_found(self):
        result = json.loads(self.service.update_limit("999", 5000.00))
        self.assertEqual(result["status"], "error")
        self.assertIn("não encontrado", result["message"])

    @patch("builtins.input", return_value="não")
    def test_update_limit_cancelled_by_user(self, _mock_input):
        result = json.loads(self.service.update_limit("222", 8000.00))
        self.assertEqual(result["status"], "error")
        self.assertIn("cancelada", result["message"])
        self.assertEqual(self.mock_db["222"]["limite_cartao"], 1000.00)

    @patch("builtins.input", return_value="sim")
    def test_update_limit_persists_in_db(self, _mock_input):
        """Verifica que a atualização realmente muda o valor no DB."""
        self.service.update_limit("222", 3000.00)
        result = json.loads(self.service.get_limit("222"))
        self.assertEqual(result["data"]["limite_cartao"], 3000.00)

    @patch("builtins.input", return_value="sim")
    def test_update_limit_does_not_affect_other_clients(self, _mock_input):
        """Garante que alterar limite de um cliente não afeta outro."""
        self.service.update_limit("222", 9000.00)
        result_333 = json.loads(self.service.get_limit("333"))
        self.assertEqual(result_333["data"]["limite_cartao"], 5000.00)


if __name__ == "__main__":
    unittest.main()
