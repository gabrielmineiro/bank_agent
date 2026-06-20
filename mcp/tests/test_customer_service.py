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
            }
        }
        self.service = CustomerService(self.mock_db)

    def test_get_profile_success(self):
        result_json = self.service.get_profile("111")
        result = json.loads(result_json)
        self.assertEqual(result["customer_id"], "111")
        self.assertEqual(result["segment"], "Varejo")
        self.assertEqual(result["credit_score"], 500)

    def test_get_profile_not_found(self):
        result_json = self.service.get_profile("999")
        result = json.loads(result_json)
        self.assertIn("erro", result)
        self.assertEqual(result["erro"], "Cliente não encontrado.")

if __name__ == '__main__':
    unittest.main()
