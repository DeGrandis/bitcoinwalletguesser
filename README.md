# Solana Address Balance Checker
Check SOL balances for addresses you provide. The tool does not generate wallets or handle private keys.

## Setup

```bash
python -m pip install -r requirements.txt
```

Create a text file such as `addresses.txt` with one public address per line. Blank lines and comments beginning with `#` are ignored.

## Run

```bash
python .\solanaguesser.py --addresses .\addresses.txt
```

The checker waits one second between requests by default. To use a different RPC provider, specify its URL:

```bash
python .\solanaguesser.py --addresses .\addresses.txt --rpc-url https://your-rpc-endpoint
```

When the RPC provider returns HTTP 429 or a server error, the checker honors `Retry-After` when provided; otherwise, it uses bounded exponential backoff and stops after five retries.
