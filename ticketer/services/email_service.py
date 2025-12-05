"""Email service interface and implementations."""

from typing import Protocol


class EmailService(Protocol):
    """Interface for email service (to be mocked in tests)."""

    def send_confirmation_email(self, to: str, order_id: int) -> bool:
        """Send order confirmation email."""
        ...


class FakeEmailService:
    """
    Fake email service for testing.

    Stores sent emails in a list instead of actually sending them.
    """

    def __init__(self):
        self.sent_emails: list[dict] = []

    def send_confirmation_email(self, to: str, order_id: int) -> bool:
        """Record a fake email send."""
        self.sent_emails.append({"to": to, "order_id": order_id, "type": "confirmation"})
        return True

    def clear(self):
        """Clear sent emails (useful for test setup)."""
        self.sent_emails.clear()


class RealEmailService:
    """Real email service (would use SMTP or external API)."""

    def __init__(self, smtp_host: str, smtp_port: int):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send_confirmation_email(self, to: str, order_id: int) -> bool:
        """Send a real confirmation email (placeholder)."""
        # In real implementation, would send via SMTP
        print(f"Sending email to {to} for order {order_id}")
        return True
