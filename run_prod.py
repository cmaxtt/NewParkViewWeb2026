"""Production entry point — serves Flask via Waitress.

Binds ONLY to loopback (localhost admin access) and the machine's
Tailscale IP — NOT 0.0.0.0 — so the site is reachable over the
Tailscale mesh network without being exposed on the LAN.

Tailscale IP resolution order:
    1. `tailscale ip -4` CLI (live detection)
    2. PARKVIEW_TAILSCALE_IP environment variable (explicit override)
    3. Not detected -> bind loopback only (safe default, no exposure)

Logging: rotating file (parkview_app.log, 5 MB x 3) + stderr.

Usage:
    python run_prod.py

Access:
    Local:      http://127.0.0.1:5000
    Tailscale:  http://<this-machine's-tailscale-ip>:5000
    Admin:      http://127.0.0.1:5000/admin/login
    Health:     http://127.0.0.1:5000/healthz
"""
import logging
import os
import socket
from logging.handlers import RotatingFileHandler

from waitress import serve
from app import app, init_db


def detect_tailscale_ip():
    """Return this machine's current Tailscale IPv4 (100.x.y.z), if any."""
    try:
        import subprocess
        out = subprocess.run(
            ["tailscale", "ip", "-4"], capture_output=True, text=True, timeout=10
        ).stdout.strip()
        for line in out.splitlines():
            ip = line.strip()
            if ip.startswith("100."):
                return ip
    except Exception:
        pass
    return None


def setup_logging():
    """Rotating file log (5 MB x 3) plus the existing stderr stream."""
    handler = RotatingFileHandler(
        "parkview_app.log", maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)


if __name__ == "__main__":
    setup_logging()
    with app.app_context():
        init_db()

    tailscale_ip = detect_tailscale_ip() or os.environ.get("PARKVIEW_TAILSCALE_IP") or None
    binds = ["127.0.0.1:5000"]
    if tailscale_ip:
        binds.append(f"{tailscale_ip}:5000")

    print("=" * 52)
    print("  Park View Drugs - Production Server")
    print("=" * 52)
    print(f"  Local:      http://127.0.0.1:5000")
    print(f"  Tailscale:  http://{tailscale_ip or '(not detected - loopback only)'}:5000")
    print(f"  Admin:      http://127.0.0.1:5000/admin/login")
    print(f"  Health:     http://127.0.0.1:5000/healthz")
    print("=" * 52)
    print("  Server: Waitress (threads=4)")
    print(f"  Bind:   {', '.join(binds)} (no LAN exposure)")
    print("=" * 52)
    serve(app, listen=binds, threads=4)
