import argparse
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import requests
from solders.pubkey import Pubkey

RPC_URL = "https://api.mainnet-beta.solana.com"
LAMPORTS_PER_SOL = 1_000_000_000
MAX_RETRIES = 5
MAX_BACKOFF_SECONDS = 60


def load_addresses(path):
    addresses = []
    seen = set()

    with open(path, encoding="utf-8") as address_file:
        for line_number, line in enumerate(address_file, start=1):
            address = line.partition("#")[0].strip()
            if not address:
                continue

            try:
                parsed = Pubkey.from_string(address)
            except ValueError as exc:
                raise ValueError(
                    f"Invalid Solana address on line {line_number}: {address}"
                ) from exc

            normalized = str(parsed)
            if normalized not in seen:
                addresses.append(normalized)
                seen.add(normalized)

    if not addresses:
        raise ValueError(f"No Solana addresses found in {path}")
    return addresses


def _retry_after_seconds(value):
    if not value:
        return None

    try:
        return max(0, float(value))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            return max(0, (retry_at - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None


def get_balance(public_key, rpc_url=RPC_URL, retries=MAX_RETRIES, session=None):
    http = session or requests
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getBalance",
        "params": [public_key],
    }

    for attempt in range(retries + 1):
        try:
            response = http.post(rpc_url, json=payload, timeout=20)
        except requests.RequestException:
            if attempt == retries:
                raise
            delay = min(2**attempt, MAX_BACKOFF_SECONDS)
            print(f"RPC request failed; retrying in {delay} seconds.")
            time.sleep(delay)
            continue

        if response.status_code == 429 or response.status_code >= 500:
            if attempt == retries:
                response.raise_for_status()
            retry_after = _retry_after_seconds(response.headers.get("Retry-After"))
            delay = retry_after if retry_after is not None else min(
                2**attempt, MAX_BACKOFF_SECONDS
            )
            print(f"RPC returned HTTP {response.status_code}; retrying in {delay:g} seconds.")
            time.sleep(delay)
            continue

        response.raise_for_status()
        data = response.json()
        if "error" in data:
            raise RuntimeError(f"Solana RPC error: {data['error']}")
        return data["result"]["value"]


def check_addresses(addresses, rpc_url=RPC_URL, request_interval=1.0):
    for index, address in enumerate(addresses):
        balance = get_balance(address, rpc_url)
        print(f"{address}: {balance} lamports ({balance / LAMPORTS_PER_SOL:.9f} SOL)")
        if index < len(addresses) - 1 and request_interval > 0:
            time.sleep(request_interval)


def main():
    parser = argparse.ArgumentParser(
        description="Check balances for Solana addresses you provide."
    )
    parser.add_argument(
        "--addresses",
        required=True,
        help="Text file containing one Solana public address per line.",
    )
    parser.add_argument("--rpc-url", default=RPC_URL, help="Solana RPC endpoint to query.")
    parser.add_argument(
        "--request-interval",
        type=float,
        default=1.0,
        help="Seconds to wait between address checks (default: 1).",
    )
    args = parser.parse_args()

    if args.request_interval < 0:
        parser.error("--request-interval must be zero or greater.")

    try:
        addresses = load_addresses(args.addresses)
        check_addresses(addresses, args.rpc_url, args.request_interval)
    except (OSError, ValueError, requests.RequestException, RuntimeError, KeyError) as exc:
        parser.exit(1, f"Error: {exc}\n")
    return 0


if __name__ == "__main__":
    print("--Running Solana address balance checker v1.0--")
    raise SystemExit(main())
