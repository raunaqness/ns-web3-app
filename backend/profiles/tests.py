"""
profiles/tests.py — Unit tests for the ENS service module.

Run with:
    ./venv/bin/python manage.py test profiles

To also run the live integration test (hits real Infura):
    RUN_INTEGRATION_TESTS=1 ./venv/bin/python manage.py test profiles
"""

import os
from unittest.mock import MagicMock, patch, call
from django.test import TestCase


# ---------------------------------------------------------------------------
# Helpers to build fake Web3 contract mocks
# ---------------------------------------------------------------------------

VITALIK_OWNER = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
VITALIK_RESOLVER = "0x231b0Ee14048e9dCcD1d247744d114a4EB5E8E63"
NULL_ADDRESS = "0x0000000000000000000000000000000000000000"


def _build_mock_w3(
    owner=VITALIK_OWNER,
    resolver=VITALIK_RESOLVER,
    text_records=None,
    eth_addr=VITALIK_OWNER,
    btc_raw=b"",
    sol_raw=b"",
    expires_ts=1777000000,
    is_wrapped=False,
    connected=True,
):
    """Return a fully-mocked Web3 instance simulating vitalik.eth data."""
    if text_records is None:
        text_records = {
            "avatar": "https://euc.li/vitalik.eth",
            "description": "mi pinxe lo crino tcati",
            "url": "https://vitalik.ca",
            "com.twitter": "VitalikButerin",
            "com.github": "vbuterin",
            "com.discord": "",
            "email": "",
            "name": "Vitalik Buterin",
        }

    w3 = MagicMock()
    w3.is_connected.return_value = connected

    # Registry contract
    registry_contract = MagicMock()
    registry_contract.functions.owner.return_value.call.return_value = owner
    registry_contract.functions.resolver.return_value.call.return_value = resolver

    # Resolver contract — text() maps key -> value
    resolver_contract = MagicMock()
    resolver_contract.functions.text.side_effect = lambda node, key: MagicMock(
        call=MagicMock(return_value=text_records.get(key, ""))
    )
    # addr() overload for ETH (no coin type)
    resolver_contract.functions.addr.return_value.call.return_value = eth_addr

    # Registrar contract
    registrar_contract = MagicMock()
    registrar_contract.functions.nameExpires.return_value.call.return_value = expires_ts

    # Name wrapper contract
    wrapper_contract = MagicMock()
    wrapper_contract.functions.isWrapped.return_value.call.return_value = is_wrapped

    # Route w3.eth.contract() calls by address
    def contract_factory(address=None, abi=None):
        addr_lower = (address or "").lower()
        if "00000000000c2e" in addr_lower:   # ENS Registry
            return registry_contract
        if addr_lower == resolver.lower():   # Public Resolver
            return resolver_contract
        if "253553366da854" in addr_lower:   # ETH Registrar
            return registrar_contract
        if "d4416b13d2b3a9" in addr_lower:   # Name Wrapper
            return wrapper_contract
        return MagicMock()

    w3.eth.contract.side_effect = contract_factory
    w3.to_checksum_address = lambda x: x  # passthrough
    return w3


# ---------------------------------------------------------------------------
# Unit tests (fully mocked — no network calls)
# ---------------------------------------------------------------------------

class FetchEnsProfileMockedTests(TestCase):
    """Tests for fetch_ens_profile() using mocked Web3."""

    def _call(self, ens_name="vitalik.eth", **mock_kwargs):
        mock_w3 = _build_mock_w3(**mock_kwargs)
        with patch("profiles.services._get_web3", return_value=mock_w3), \
             patch("profiles.services.Web3.to_checksum_address", side_effect=lambda x: x), \
             patch("profiles.services.Web3.keccak", return_value=b"\x00" * 32):
            from profiles.services import fetch_ens_profile
            return fetch_ens_profile(ens_name)

    def test_returns_ens_name(self):
        result = self._call("vitalik.eth")
        self.assertEqual(result["ens"], "vitalik.eth")

    def test_returns_owner_address(self):
        result = self._call("vitalik.eth")
        self.assertEqual(result["owner"], VITALIK_OWNER)

    def test_returns_avatar(self):
        result = self._call("vitalik.eth")
        self.assertEqual(result["avatar"], "https://euc.li/vitalik.eth")

    def test_returns_description(self):
        result = self._call("vitalik.eth")
        self.assertEqual(result["description"], "mi pinxe lo crino tcati")

    def test_returns_url(self):
        result = self._call("vitalik.eth")
        self.assertEqual(result["url"], "https://vitalik.ca")

    def test_returns_twitter(self):
        result = self._call("vitalik.eth")
        self.assertEqual(result["socials"]["twitter"], "VitalikButerin")

    def test_returns_github(self):
        result = self._call("vitalik.eth")
        self.assertEqual(result["socials"]["github"], "vbuterin")

    def test_empty_socials_not_included(self):
        """Discord and email are empty strings — should not appear in socials."""
        result = self._call("vitalik.eth")
        self.assertNotIn("discord", result["socials"])

    def test_returns_eth_wallet(self):
        result = self._call("vitalik.eth")
        self.assertEqual(result["wallets"]["ETH"], VITALIK_OWNER)

    def test_returns_resolver_in_metadata(self):
        result = self._call("vitalik.eth")
        self.assertEqual(result["metadata"]["resolver"], VITALIK_RESOLVER)

    def test_returns_expiry_in_metadata(self):
        result = self._call("vitalik.eth")
        self.assertIn("expiry", result["metadata"])
        self.assertRegex(result["metadata"]["expiry"], r"\d{4}-\d{2}-\d{2}")

    def test_returns_wrapped_false(self):
        result = self._call("vitalik.eth")
        self.assertFalse(result["metadata"]["wrapped"])

    def test_no_error_for_valid_name(self):
        result = self._call("vitalik.eth")
        self.assertIsNone(result["error"])

    def test_error_when_no_owner(self):
        """A name with no owner (null address) should return an error."""
        result = self._call("nonexistent.eth", owner=NULL_ADDRESS)
        self.assertIsNotNone(result["error"])
        self.assertIsNone(result["owner"])

    def test_error_when_not_connected(self):
        """Should return an error dict when Web3 cannot connect."""
        result = self._call("vitalik.eth", connected=False)
        self.assertIsNotNone(result["error"])
        self.assertIn("connect", result["error"].lower())

    def test_result_has_required_keys(self):
        """Result dict must always contain all expected top-level keys."""
        result = self._call("vitalik.eth")
        for key in ("ens", "owner", "avatar", "description", "url", "socials", "wallets", "metadata", "error"):
            self.assertIn(key, result, f"Missing key: {key}")


# ---------------------------------------------------------------------------
# Integration test — runs against real Infura (skipped by default)
# ---------------------------------------------------------------------------

class FetchEnsProfileIntegrationTest(TestCase):
    """
    Live integration test. Skipped unless RUN_INTEGRATION_TESTS=1 is set.

    Usage:
        RUN_INTEGRATION_TESTS=1 ./venv/bin/python manage.py test profiles.tests.FetchEnsProfileIntegrationTest
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not os.environ.get("RUN_INTEGRATION_TESTS"):
            import unittest
            raise unittest.SkipTest("Set RUN_INTEGRATION_TESTS=1 to run live tests.")

    def test_vitalik_eth_live(self):
        """Fetch vitalik.eth from mainnet and assert key fields are present."""
        from profiles.services import fetch_ens_profile
        result = fetch_ens_profile("vitalik.eth")

        self.assertIsNone(result["error"], f"Unexpected error: {result['error']}")
        self.assertEqual(result["ens"], "vitalik.eth")
        # Owner is Vitalik's well-known address
        self.assertEqual(
            result["owner"].lower(),
            "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",
        )
        self.assertIsNotNone(result["avatar"])
        self.assertIsNotNone(result["description"])
        self.assertEqual(result["url"], "https://vitalik.ca")
        self.assertIn("twitter", result["socials"])
        self.assertEqual(result["socials"]["twitter"], "VitalikButerin")
        self.assertIn("github", result["socials"])
        self.assertIn("ETH", result["wallets"])
        self.assertEqual(
            result["wallets"]["ETH"].lower(),
            "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",
        )
        self.assertIn("resolver", result["metadata"])
        self.assertIn("wrapped", result["metadata"])
