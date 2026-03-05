"""
profiles/services.py — ENS resolution service using web3.py

Fetches all available data for an ENS name from the Ethereum mainnet:
  - Owner address
  - Text records (avatar, description, url, twitter, github, discord, email)
  - Coin addresses (ETH, BTC, SOL via EIP-2304 coin-type lookups)
  - Metadata (resolver address, expiry/registration date, wrapped state)
"""

from __future__ import annotations

import datetime
import logging
import requests

from django.conf import settings
from web3 import Web3

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# ENS Registry & Public Resolver ABIs (minimal — only what we need)
# ---------------------------------------------------------------------------

# ENS Registry — to get the resolver for a node
ENS_REGISTRY_ADDRESS = "0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e"
ENS_REGISTRY_ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "node", "type": "bytes32"}],
        "name": "resolver",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "node", "type": "bytes32"}],
        "name": "owner",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "node", "type": "bytes32"}],
        "name": "ttl",
        "outputs": [{"internalType": "uint64", "name": "", "type": "uint64"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# Public Resolver — text records, addr, contenthash
RESOLVER_ABI = [
    {
        "inputs": [
            {"internalType": "bytes32", "name": "node", "type": "bytes32"},
            {"internalType": "string", "name": "key", "type": "string"},
        ],
        "name": "text",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "node", "type": "bytes32"},
            {"internalType": "uint256", "name": "coinType", "type": "uint256"},
        ],
        "name": "addr",
        "outputs": [{"internalType": "bytes", "name": "", "type": "bytes"}],
        "stateMutability": "view",
        "type": "function",
    },
    # addr(bytes32) — coin type 60 (ETH) shorthand
    {
        "inputs": [{"internalType": "bytes32", "name": "node", "type": "bytes32"}],
        "name": "addr",
        "outputs": [{"internalType": "address payable", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# ETH Registrar Controller — for expiry info
ETH_REGISTRAR_ADDRESS = "0x253553366Da8546fC250F225fe3d25d0C782303b"
ETH_REGISTRAR_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "name", "type": "string"}],
        "name": "nameExpires",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# Name Wrapper — to check if name is wrapped
NAME_WRAPPER_ADDRESS = "0xD4416b13d2b3a9aBae7AcD5D6C2BbDBE25686401"
NAME_WRAPPER_ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "node", "type": "bytes32"}],
        "name": "isWrapped",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function",
    },
]

# EIP-2304 coin types
COIN_TYPE_ETH = 60
COIN_TYPE_BTC = 0
COIN_TYPE_SOL = 501


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_web3() -> Web3:
    """Return a connected Web3 instance."""
    provider_url = settings.WEB3_PROVIDER_URL
    if not provider_url:
        raise ValueError("WEB3_PROVIDER_URL is not configured in settings.")
    w3 = Web3(Web3.HTTPProvider(provider_url, request_kwargs={"timeout": 10}))
    return w3


def _namehash(name: str) -> bytes:
    """Compute the ENS namehash for a given name."""
    node = b"\x00" * 32
    if name:
        labels = name.split(".")
        for label in reversed(labels):
            label_hash = Web3.keccak(text=label)
            node = Web3.keccak(node + label_hash)
    return node


def _bytes_to_btc_address(raw: bytes) -> str | None:
    """Convert raw bytes from addr(bytes32, 0) to a bech32 BTC address string."""
    if not raw:
        return None
    try:
        return raw.decode("utf-8")
    except Exception:
        return raw.hex() if raw else None


def _bytes_to_sol_address(raw: bytes) -> str | None:
    """Convert raw 32-byte Solana pubkey to base58 string."""
    if not raw or len(raw) != 32:
        return None
    try:
        import base58  # optional dependency
        return base58.b58encode(raw).decode()
    except ImportError:
        return raw.hex()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Main service function
# ---------------------------------------------------------------------------

def _fetch_etherscan_data(action: str, address: str, extra_params=None):
    """Helper to fetch data from Etherscan API v2."""
    api_key = settings.ETHERSCAN_API_KEY
    if not api_key:
        return None
    
    url = "https://api.etherscan.io/v2/api"
    params = {
        "chainid": "1",
        "module": "account",
        "action": action,
        "address": address,
        "apikey": api_key,
    }
    if extra_params:
        params.update(extra_params)
        
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "1":
            return data.get("result")
    except Exception as e:
        logger.debug("Etherscan API error for %s: %s", action, e)
    return None

def fetch_ens_profile(ens_name: str) -> dict:
    """
    Resolve an ENS name and fetch all its associated data.

    Returns a dict with keys:
        ens, owner, avatar, description, url, socials, wallets, metadata, error
    """
    result: dict = {
        "ens": ens_name,
        "owner": None,
        "avatar": None,
        "description": None,
        "url": None,
        "socials": {},
        "wallets": {},
        "metadata": {},
        "etherscan": None,
        "error": None,
    }

    try:
        w3 = _get_web3()

        if not w3.is_connected():
            result["error"] = "Could not connect to Ethereum node."
            return result

        node = _namehash(ens_name)

        # --- Registry ---
        registry = w3.eth.contract(
            address=Web3.to_checksum_address(ENS_REGISTRY_ADDRESS),
            abi=ENS_REGISTRY_ABI,
        )

        owner_raw = registry.functions.owner(node).call()
        null_address = "0x0000000000000000000000000000000000000000"

        if owner_raw == null_address:
            result["error"] = f"'{ens_name}' does not exist or has no owner."
            return result

        result["owner"] = owner_raw

        resolver_address = registry.functions.resolver(node).call()

        if resolver_address == null_address:
            result["error"] = f"No resolver set for '{ens_name}'."
            return result

        result["metadata"]["resolver"] = resolver_address

        # --- Resolver: text records ---
        resolver = w3.eth.contract(
            address=Web3.to_checksum_address(resolver_address),
            abi=RESOLVER_ABI,
        )

        text_keys = {
            "avatar": "avatar",
            "description": "description",
            "url": "url",
            "twitter": "com.twitter",
            "github": "com.github",
            "discord": "com.discord",
            "email": "email",
            "name": "name",
        }

        for field, key in text_keys.items():
            try:
                value = resolver.functions.text(node, key).call()
                if value:
                    if field in ("twitter", "github", "discord"):
                        result["socials"][field] = value
                    elif field == "avatar":
                        result["avatar"] = value
                    elif field == "url":
                        result["url"] = value
                    elif field == "description":
                        result["description"] = value
            except Exception as e:
                logger.debug("text(%s) failed: %s", key, e)

        # --- Resolver: coin addresses ---
        # ETH address (coin type 60)
        try:
            eth_addr = resolver.functions.addr(node).call()
            if eth_addr and eth_addr != null_address:
                result["wallets"]["ETH"] = eth_addr
        except Exception as e:
            logger.debug("addr(ETH) failed: %s", e)

        # BTC (coin type 0)
        try:
            btc_raw = resolver.functions.addr(node, COIN_TYPE_BTC).call()
            if btc_raw:
                btc_str = _bytes_to_btc_address(btc_raw)
                if btc_str:
                    result["wallets"]["BTC"] = btc_str
        except Exception as e:
            logger.debug("addr(BTC) failed: %s", e)

        # SOL (coin type 501)
        try:
            sol_raw = resolver.functions.addr(node, COIN_TYPE_SOL).call()
            if sol_raw:
                sol_str = _bytes_to_sol_address(sol_raw)
                if sol_str:
                    result["wallets"]["SOL"] = sol_str
        except Exception as e:
            logger.debug("addr(SOL) failed: %s", e)

        # --- Expiry date from ETH Registrar ---
        try:
            registrar = w3.eth.contract(
                address=Web3.to_checksum_address(ETH_REGISTRAR_ADDRESS),
                abi=ETH_REGISTRAR_ABI,
            )
            # Strip the .eth suffix for the registrar lookup
            label = ens_name.removesuffix(".eth")
            expires_ts = registrar.functions.nameExpires(label).call()
            if expires_ts:
                expiry_dt = datetime.datetime.fromtimestamp(expires_ts, tz=datetime.timezone.utc)
                result["metadata"]["expiry"] = expiry_dt.strftime("%Y-%m-%d")
        except Exception as e:
            logger.debug("nameExpires failed: %s", e)

        # --- Wrapped state ---
        try:
            wrapper = w3.eth.contract(
                address=Web3.to_checksum_address(NAME_WRAPPER_ADDRESS),
                abi=NAME_WRAPPER_ABI,
            )
            result["metadata"]["wrapped"] = wrapper.functions.isWrapped(node).call()
        except Exception as e:
            logger.debug("isWrapped failed: %s", e)
            result["metadata"]["wrapped"] = False

        # --- Etherscan API Logic ---
        if "ETH" in result.get("wallets", {}):
            eth_address = result["wallets"]["ETH"]
            try:
                # Balance
                bal_wei_str = _fetch_etherscan_data("balance", eth_address, {"tag": "latest"})
                balance_eth = None
                if bal_wei_str is not None:
                    try:
                        balance_eth = round(int(bal_wei_str) / 10**18, 4)
                    except Exception:
                        pass
                
                # Transactions
                tx_list = _fetch_etherscan_data(
                    "txlist", 
                    eth_address, 
                    {"startblock": 0, "endblock": 99999999, "page": 1, "offset": 10, "sort": "desc"}
                )
                
                # Internal Transactions
                internal_tx_list = _fetch_etherscan_data(
                    "txlistinternal", 
                    eth_address, 
                    {"page": 1, "offset": 10, "sort": "desc"}
                )
                
                result["etherscan"] = {
                    "balance": balance_eth,
                    "transactions": tx_list if isinstance(tx_list, list) else [],
                    "internal_transactions": internal_tx_list if isinstance(internal_tx_list, list) else []
                }
            except Exception as e:
                logger.debug("Etherscan API fetch failed: %s", e)

    except Exception as e:
        logger.exception("Unexpected error fetching ENS profile for %s", ens_name)
        result["error"] = f"Unexpected error: {str(e)}"

    return result
