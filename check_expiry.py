#!/usr/bin/env python3
"""
Expiry Tracker — denná kontrola dátumov spotreby.
Spúšťa sa cez GitHub Actions každý deň.
Číta products.json a posiela email ak niečo expiruje do 30 dní.
"""

import json
import os
import smtplib
import sys
from datetime import datetime, date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path


def days_until(date_str: str) -> int:
    """Počet dní do expirácie."""
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (target - date.today()).days
    except ValueError:
        return 999


def load_products() -> list:
    """Načíta produkty z products.json."""
    path = Path("products.json")
    if not path.exists():
        print("⚠️  products.json neexistuje — žiadne produkty na kontrolu.")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_expiring(products: list, max_days: int = 30) -> list:
    """Vráti produkty, ktorým zostáva menej ako max_days dní."""
    expiring = []
    for p in products:
        if not p.get("expiry"):
            continue
        days = days_until(p["expiry"])
        if days <= max_days:
            expiring.append({**p, "_days": days})
    return sorted(expiring, key=lambda x: x["_days"])


def format_email_html(expiring: list) -> str:
    """Vytvorí HTML email s prehľadom."""
    today_str = date.today().strftime("%d.%m.%Y")

    rows = ""
    for p in expiring:
        d = p["_days"]
        if d < 0:
            status = "⛔ EXPIROVANÉ"
            color = "#ef4444"
            days_text = f"{abs(d)} dní po expirácii"
        elif d == 0:
            status = "🔴 DNES"
            color = "#ef4444"
            days_text = "Dnes expiruje!"
        elif d <= 7:
            status = "🔴 KRITICKÉ"
            color = "#f97316"
            days_text = f"{d} dní"
        else:
            status = "🟠 Blíži sa"
            color = "#eab308"
            days_text = f"{d} dní"

        expiry_formatted = datetime.strptime(p["expiry"], "%Y-%m-%d").strftime("%d.%m.%Y")

        rows += f"""
        <tr>
          <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:14px;">
            <span style="color:{color};font-weight:600;">{status}</span>
          </td>
          <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:14px;font-weight:500;">
            {p.get('name', 'Neznámy')}
          </td>
          <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:14px;color:#666;">
            {expiry_formatted}
          </td>
          <td style="padding:10px 12px;border-bottom:1px solid #f0f0f0;font-size:14px;font-weight:600;color:{color};">
            {days_text}
          </td>
        </tr>"""

    expired_count = sum(1 for p in expiring if p["_days"] < 0)
    critical_count = sum(1 for p in expiring if 0 <= p["_days"] <= 7)
    warning_count = sum(1 for p in expiring if 7 < p["_days"] <= 30)

    return f"""
    <div style="font-family:'Segoe UI',Arial,sans-serif;max-width:600px;margin:0 auto;background:#ffffff;">
      <div style="background:linear-gradient(135deg,#1e293b,#0f172a);padding:24px;border-radius:12px 12px 0 0;">
        <h1 style="color:#fff;margin:0;font-size:22px;">📦 Expiry Tracker</h1>
        <p style="color:#94a3b8;margin:4px 0 0;font-size:14px;">Denný prehľad — {today_str}</p>
      </div>

      <div style="padding:20px;background:#f8fafc;border:1px solid #e2e8f0;">
        <div style="display:flex;gap:12px;text-align:center;">
          <div style="flex:1;padding:12px;background:#fef2f2;border-radius:8px;">
            <div style="font-size:24px;font-weight:700;color:#ef4444;">{expired_count}</div>
            <div style="font-size:11px;color:#666;">Expirované</div>
          </div>
          <div style="flex:1;padding:12px;background:#fff7ed;border-radius:8px;">
            <div style="font-size:24px;font-weight:700;color:#f97316;">{critical_count}</div>
            <div style="font-size:11px;color:#666;">Kritické</div>
          </div>
          <div style="flex:1;padding:12px;background:#fefce8;border-radius:8px;">
            <div style="font-size:24px;font-weight:700;color:#eab308;">{warning_count}</div>
            <div style="font-size:11px;color:#666;">Do 30 dní</div>
          </div>
        </div>
      </div>

      <table style="width:100%;border-collapse:collapse;background:#fff;">
        <thead>
          <tr style="background:#f8fafc;">
            <th style="padding:10px 12px;text-align:left;font-size:12px;color:#64748b;font-weight:600;">Stav</th>
            <th style="padding:10px 12px;text-align:left;font-size:12px;color:#64748b;font-weight:600;">Produkt</th>
            <th style="padding:10px 12px;text-align:left;font-size:12px;color:#64748b;font-weight:600;">Expirácia</th>
            <th style="padding:10px 12px;text-align:left;font-size:12px;color:#64748b;font-weight:600;">Zostáva</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>

      <div style="padding:16px;text-align:center;color:#94a3b8;font-size:12px;border-top:1px solid #e2e8f0;">
        Celkom {len(expiring)} produktov vyžaduje pozornosť · Odoslané automaticky z Expiry Tracker
      </div>
    </div>"""


def send_email(html_body: str, product_count: int):
    """Odošle email cez SMTP."""
    email_to = os.environ.get("EMAIL_TO")
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if not all([email_to, smtp_user, smtp_password]):
        print("❌ Chýbajú SMTP credentials v GitHub Secrets!")
        print("   Potrebné: EMAIL_TO, SMTP_USER, SMTP_PASSWORD")
        sys.exit(1)

    today_str = date.today().strftime("%d.%m.%Y")
    subject = f"⚠️ Expiry Tracker — {product_count} produktov vyžaduje pozornosť ({today_str})"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = email_to
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [email_to], msg.as_string())

    print(f"✅ Email odoslaný na {email_to} ({product_count} produktov)")


def main():
    print(f"🔍 Kontrolujem expirácie... ({date.today()})")

    products = load_products()
    if not products:
        print("📭 Žiadne produkty. Končím.")
        return

    print(f"📦 Celkom {len(products)} produktov")

    expiring = get_expiring(products, max_days=30)
    if not expiring:
        print("✅ Žiadne produkty neexpirujú do 30 dní. Končím.")
        return

    print(f"⚠️  {len(expiring)} produktov expiruje do 30 dní!")

    for p in expiring:
        d = p["_days"]
        icon = "⛔" if d < 0 else "🔴" if d <= 7 else "🟠"
        print(f"  {icon} {p.get('name','?')} — {d}d")

    html = format_email_html(expiring)
    send_email(html, len(expiring))


if __name__ == "__main__":
    main()
