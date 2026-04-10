# 🏪 Token Vendor

A decentralized token vending machine built with **Vyper** and deployed on **zkSync Sepolia**.
Users can buy and sell ERC20 tokens directly against ETH at a fixed rate — fully on-chain, trustlessly.

---

## ✨ Features

- **Buy tokens** — Send ETH, receive tokens at a fixed rate (100 tokens / ETH)
- **Sell tokens** — Send tokens back, receive ETH proportionally
- **Owner withdrawal** — Contract owner can withdraw accumulated ETH
- **Reentrancy protection** — All state-changing functions use `@nonreentrant`
- **CEI pattern** — Strict Checks → Effects → Interactions ordering throughout

---

## 🛠️ Stack

| Tool | Role |
|---|---|
| [Vyper](https://vyperlang.org/) `^0.4.0` | Smart contract language |
| [Moccasin](https://github.com/Cyfrin/moccasin) | Python-based testing & deployment framework |
| [uv](https://github.com/astral-sh/uv) | Python package manager |
| [Snekmate](https://github.com/pcaversaccio/snekmate) | Vyper ERC20 implementation |
| [zkSync Sepolia](https://sepolia.explorer.zksync.io/) | Testnet deployment |
| [Hypothesis](https://hypothesis.readthedocs.io/) | Stateful fuzz testing |

---

## ⚡ Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/ladieweb3/tokenVendor
cd tokenVendor
```

### 2. Install dependencies with uv

```bash
uv sync
```

### 3. Set up environment variables

```bash
cp .env.example .env
# Fill in your PRIVATE_KEY and RPC_URL
```

### 4. Deploy

```bash
mox run deploy_token
mox run deploy_vendor_engine
```

### 5. Compile

```bash
mox compile

```

---

## 🧪 Tests

### Unit tests

```bash
mox test tests/unit/
```

### Fuzz tests

```bash
mox test tests/fuzz/
```

The fuzz suite uses **Hypothesis stateful testing** to generate random sequences of:
- `buyTokens` — random users buying with random ETH amounts
- `sellTokens` — random users selling random token amounts
- `withdraw` — owner withdrawing ETH

**Invariants checked after every action:**
- Vendor balance is `0` after `withdraw`

---

## 🔐 Security

- `@nonreentrant` on all state-changing functions
- CEI pattern enforced throughout (`Checks → Effects → Log → Interactions `)
- No floating pragma — pinned Vyper version

---


## 📄 License

MIT