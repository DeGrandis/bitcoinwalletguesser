# Solana Wallet Guesser
A fun tool to randomly generate Solana wallets and check whether any of them have a non-zero balance on the mainnet RPC.

## Will I ever find a wallet?
The Solana address space is enormous. Random wallet discovery is effectively a probabilistic lottery, but a lucky hit is possible.

## Why this version is different
This repo now uses Solana keypairs instead of Bitcoin wallet generation and checks addresses with the public Solana JSON-RPC API.

## How to run
Clone this repo and run it:

```bash
python .\solanaguesser.py --once --wallets 10
```

You can keep it running in a loop with:

```bash
python .\solanaguesser.py --wallets 50 --sleep 5
```

The script will print any wallet with a positive balance and exit early when you use `--once`.

