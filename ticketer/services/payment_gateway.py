"""Payment gateway interface and implementations."""

from dataclasses import dataclass
from typing import Protocol
from decimal import Decimal


@dataclass
class PaymentResult:
    """Result of a payment transaction."""

    success: bool
    transaction_id: str | None = None
    error_message: str | None = None


class PaymentGateway(Protocol):
    """Interface for payment gateway (to be mocked in tests)."""

    def process_payment(self, amount: Decimal, token: str) -> PaymentResult:
        """Process a payment."""
        ...


class FakePaymentGateway:
    """
    Fake payment gateway for testing.

    Returns success for token 'ok' or 'success', failure otherwise.
    """

    def process_payment(self, amount: Decimal, token: str) -> PaymentResult:
        """Process a fake payment."""
        if token in ("ok", "success"):
            return PaymentResult(success=True, transaction_id=f"fake_txn_{token}")
        else:
            return PaymentResult(success=False, error_message="Payment failed")


class RealPaymentGateway:
    """Real payment gateway (would call external API)."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def process_payment(self, amount: Decimal, token: str) -> PaymentResult:
        """Process a real payment (placeholder)."""
        # In real implementation, would call external payment API
        # For now, just simulate success
        return PaymentResult(success=True, transaction_id=f"real_txn_{token[:8]}")
