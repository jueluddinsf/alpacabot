"""Reporting utilities for daily/weekly summaries."""

from __future__ import annotations

import smtplib
from email.mime.text import MIMEText
from typing import Iterable

from core.config import settings


def generate_report(signals: list, trades: list, pnl: float) -> str:
    """Create a Markdown report summarizing activity."""
    lines = ["# Market Report", "", f"Total PnL: {pnl:.2f}", "", "## Signals"]
    for sig in signals:
        lines.append(f"- {sig.symbol}: {sig.direction} ({sig.confidence:.2f})")
    lines.append("\n## Trades")
    for trd in trades:
        lines.append(f"- {trd}")
    return "\n".join(lines)


def send_email(subject: str, content: str, recipients: Iterable[str]) -> None:
    """Send report via SMTP."""
    msg = MIMEText(content, "plain")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_user
    msg["To"] = ", ".join(recipients)

    with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_user, list(recipients), msg.as_string())
