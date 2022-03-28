import unittest

from chalicelib import generate_transactions
from chalicelib import transactions_as_csv


class GenerateTestCase(unittest.TestCase):
    def test_single_transaction(self):
        transactions = generate_transactions(1)
        self.assertEqual(len(transactions), 1)
        transaction = transactions[0]
        self.assertTrue(hasattr(transaction, "trans_id"))
        self.assertEqual(13, len(transaction.trans_id))
        self.assertTrue(hasattr(transaction, "trans_name"))
        self.assertFalse(hasattr(transaction, "slappy"))

    def test_transaction_batch(self):
        transactions = generate_transactions(12)
        self.assertEqual(len(transactions), 12)
        print(transactions_as_csv(transactions))


if __name__ == '__main__':
    unittest.main()
