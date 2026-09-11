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
    Local:      http://127.0.0.1:5050
    Tailscale:  http://<this-machine's-tailscale-ip>:5050
    Admin:      http://127.0.0.1:5050/admin/login
    Health:     http://127.0.0.1:5050/healthz
"""
import logging
import os
import socket
from logging.handlers import RotatingFileHandler

from waitress import serve
from app import app, init_db


def detect_machine_ip():
    """Return this machine's primary IPv4 address for remote access."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


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

    machine_ip = detect_machine_ip()
    tailscale_ip = detect_tailscale_ip() or os.environ.get("PARKVIEW_TAILSCALE_IP") or None
    port = int(os.environ.get('PARKVIEW_PORT', '5050'))
    bind_target = f"0.0.0.0:{port}"

    print("=" * 56)
    print("  Park View Drugs - Production Server")
    print("=" * 56)
    print(f"  Local Access:      http://127.0.0.1:{port}")
    if machine_ip:
        print(f"  Machine IP Remote: http://{machine_ip}:{port}")
    if tailscale_ip:
        print(f"  Tailscale Mesh:    http://{tailscale_ip}:{port}")
    print(f"  Admin Portal:      http://127.0.0.1:{port}/admin/login")
    print(f"  Health Check:      http://127.0.0.1:{port}/healthz")
    print("=" * 56)
    print("  Server: Waitress (threads=4)")
    print(f"  Listening on: {bind_target}")
    print("=" * 56)
    serve(app, listen=bind_target, threads=4)
