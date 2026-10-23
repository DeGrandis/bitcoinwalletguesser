import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from solders.keypair import Keypair

from solanaguesser import get_balance, load_addresses


class SolanaAddressCheckerTests(unittest.TestCase):
    def test_load_addresses_ignores_comments_and_duplicates(self):
        address = str(Keypair().pubkey())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "addresses.txt"
            path.write_text(f"# owned addresses\n{address}\n{address} # duplicate\n", encoding="utf-8")

            self.assertEqual(load_addresses(path), [address])

    def test_load_addresses_rejects_invalid_address(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "addresses.txt"
            path.write_text("not-an-address\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "line 1"):
                load_addresses(path)

    @patch("solanaguesser.time.sleep")
    def test_get_balance_honors_retry_after(self, sleep):
        address = str(Keypair().pubkey())
        limited_response = Mock(status_code=429, headers={"Retry-After": "3"})
        success_response = Mock(
            status_code=200,
            headers={},
            json=Mock(return_value={"result": {"value": 42}}),
        )
        session = Mock()
        session.post.side_effect = [limited_response, success_response]

        balance = get_balance(address, session=session)

        self.assertEqual(balance, 42)
        sleep.assert_called_once_with(3.0)
        self.assertEqual(session.post.call_count, 2)


if __name__ == "__main__":
    unittest.main()
