import argparse
import sys
import time

import requests
from solders.keypair import Keypair

RPC_URL = "https://api.mainnet-beta.solana.com"


def gen_wallet_info():
    keypair = Keypair()
    public_key = str(keypair.pubkey())
    secret_key = keypair.secret().hex()

    wallet = {
        "public_key": public_key,
        "private_key_hex": secret_key,
        "private_key_bytes": keypair.secret(),
    }
    return wallet


def get_balance(public_key, rpc_url=RPC_URL):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [public_key],
    }
    response = requests.post(rpc_url, json=payload, timeout=20)
    response.raise_for_status()
    data = response.json()
    return data["result"]["value"]


def guesslogic(batch_size=50, rpc_url=RPC_URL):
    walletlist = [gen_wallet_info() for _ in range(batch_size)]

    for wallet in walletlist:
        public_key = wallet["public_key"]
        balance = get_balance(public_key, rpc_url)
        if balance > 0:
            print("FOUND ACTIVE ADDRESS: " + public_key)
            print("PRIVATE KEY (hex): " + wallet["private_key_hex"])
            print("BALANCE (lamports): " + str(balance))
            print("BALANCE (SOL): " + str(balance / 1_000_000_000))
            print("RPC URL: " + rpc_url)
            print()

    return walletlist


def main():
    parser = argparse.ArgumentParser(
        description="Randomly generate Solana wallets and check them against the public RPC endpoint."
    )
    parser.add_argument("--wallets", type=int, default=50, help="Number of wallets to generate per cycle.")
    parser.add_argument("--sleep", type=float, default=5, help="Seconds to wait between cycles.")
    parser.add_argument("--rpc-url", default=RPC_URL, help="Solana RPC endpoint to query.")
    parser.add_argument("--once", action="store_true", help="Run a single cycle and exit.")
    args = parser.parse_args()

    guess_counter = 0
    while True:
        guesstime = args.sleep
        try:
            walllist = guesslogic(batch_size=args.wallets, rpc_url=args.rpc_url)
            guess_counter += len(walllist)
            print("- Wallets checked: " + str(guess_counter), end="\r")
            if args.once:
                return 0
            time.sleep(guesstime)
        except Exception as exc:
            seconds = max(5, guesstime * 12)
            print("Exception: " + str(exc))
            print("You were probably rate limited.")
            print("Sleeping " + str(seconds) + " seconds.")
            time.sleep(seconds)


if __name__ == "__main__":
    print("--Running Solana wallet Guesser v1.0--")
    sys.exit(main())
