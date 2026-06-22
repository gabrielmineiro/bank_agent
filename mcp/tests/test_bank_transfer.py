import unittest
import json
from unittest.mock import patch

from mcp.services.bank_transfer import TransferService


class TestTransferService(unittest.TestCase):
    def setUp(self):
        self.mock_db = {
            "333": {
                "saldo_conta": 1000.00,
            },
            "444": {
                "saldo_conta": 50.00,
            },
        }
        self.service = TransferService(self.mock_db)

    # ── Sucesso ──────────────────────────────────────────────────

    @patch("builtins.input", return_value="sim")
    def test_create_pix_success(self, _mock_input):
        result = json.loads(self.service.create_pix("333", 200.00, "chave-teste"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["amount"], 200.00)
        self.assertEqual(result["data"]["destination"], "chave-teste")
        self.assertEqual(result["data"]["new_balance"], 800.00)
        self.assertIn("transaction_id", result["data"])
        self.assertIn("timestamp", result["data"])

    @patch("builtins.input", return_value="sim")
    def test_create_pix_deducts_balance_in_db(self, _mock_input):
        """Verifica que o saldo é efetivamente debitado no DB."""
        self.service.create_pix("333", 300.00, "chave-abc")
        self.assertEqual(self.mock_db["333"]["saldo_conta"], 700.00)

    @patch("builtins.input", return_value="sim")
    def test_create_pix_exact_balance(self, _mock_input):
        """PIX de valor exatamente igual ao saldo deve funcionar."""
        result = json.loads(self.service.create_pix("333", 1000.00, "chave-teste"))
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"]["new_balance"], 0.00)
        self.assertEqual(self.mock_db["333"]["saldo_conta"], 0.00)

    @patch("builtins.input", return_value="sim")
    def test_create_pix_multiple_transfers(self, _mock_input):
        """Múltiplos PIX consecutivos devem debitar cumulativamente."""
        self.service.create_pix("333", 300.00, "chave-1")
        self.service.create_pix("333", 200.00, "chave-2")
        self.assertEqual(self.mock_db["333"]["saldo_conta"], 500.00)

    @patch("builtins.input", return_value="sim")
    def test_create_pix_does_not_affect_other_clients(self, _mock_input):
        """Transferência de um cliente não deve alterar saldo de outro."""
        self.service.create_pix("333", 100.00, "chave-teste")
        self.assertEqual(self.mock_db["444"]["saldo_conta"], 50.00)

    @patch("builtins.input", return_value="sim")
    def test_create_pix_generates_unique_transaction_ids(self, _mock_input):
        """Cada PIX deve gerar um transaction_id diferente."""
        result_1 = json.loads(self.service.create_pix("333", 100.00, "chave-1"))
        result_2 = json.loads(self.service.create_pix("333", 100.00, "chave-2"))
        self.assertNotEqual(
            result_1["data"]["transaction_id"],
            result_2["data"]["transaction_id"],
        )

    # ── Erros ────────────────────────────────────────────────────

    def test_create_pix_not_found(self):
        result = json.loads(self.service.create_pix("999", 200.00, "chave-teste"))
        self.assertEqual(result["status"], "error")
        self.assertIn("não encontrado", result["message"])

    def test_create_pix_insufficient_funds(self):
        result = json.loads(self.service.create_pix("333", 2000.00, "chave-teste"))
        self.assertEqual(result["status"], "error")
        self.assertIn("Saldo insuficiente", result["message"])
        self.assertEqual(self.mock_db["333"]["saldo_conta"], 1000.00)

    def test_create_pix_insufficient_funds_shows_balance(self):
        """A mensagem de erro deve incluir o saldo atual."""
        result = json.loads(self.service.create_pix("444", 100.00, "chave"))
        self.assertIn("R$ 50.00", result["message"])

    # ── Cancelamento pelo usuário ────────────────────────────────

    @patch("builtins.input", return_value="não")
    def test_create_pix_cancelled_by_user(self, _mock_input):
        result = json.loads(self.service.create_pix("333", 200.00, "chave-teste"))
        self.assertEqual(result["status"], "error")
        self.assertIn("cancelada", result["message"])
        self.assertEqual(self.mock_db["333"]["saldo_conta"], 1000.00)

    @patch("builtins.input", return_value="nao")
    def test_create_pix_cancelled_preserves_balance(self, _mock_input):
        """Cancelamento não deve alterar o saldo."""
        self.service.create_pix("333", 500.00, "chave-teste")
        self.assertEqual(self.mock_db["333"]["saldo_conta"], 1000.00)

    # ── Formato de resposta ──────────────────────────────────────

    @patch("builtins.input", return_value="sim")
    def test_response_is_valid_json(self, _mock_input):
        raw = self.service.create_pix("333", 100.00, "chave")
        parsed = json.loads(raw)
        self.assertIn("status", parsed)
        self.assertIn("message", parsed)

    def test_error_response_is_valid_json(self):
        raw = self.service.create_pix("999", 100.00, "chave")
        parsed = json.loads(raw)
        self.assertIn("status", parsed)
        self.assertIn("message", parsed)


if __name__ == "__main__":
    unittest.main()
