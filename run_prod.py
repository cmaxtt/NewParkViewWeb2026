"""Production entry point — serves Flask via Waitress on all interfaces.

Usage:
    python run_prod.py

Access:
    Local:      http://127.0.0.1:5000
    Tailscale:  http://100.104.147.60:5000
    Tailscale:  http://parkview:5000
    Network:    http://0.0.0.0:5000
"""
from waitress import serve
from app import app

TAILSCALE_IP = "100.104.147.60"

if __name__ == '__main__':
    import socket
    hostname = socket.gethostname()
    print("=" * 52)
    print("  Park View Drugs — Production Server")
    print("=" * 52)
    print(f"  Local:      http://127.0.0.1:5000")
    print(f"  Tailscale:  http://{TAILSCALE_IP}:5000")
    print(f"  Tailscale:  http://parkview:5000")
    print(f"  Hostname:   http://{hostname}:5000")
    print(f"  Admin:      http://127.0.0.1:5000/admin/login")
    print("=" * 52)
    print("  Server: Waitress (threads=4)")
    print("=" * 52)
    serve(app, host='0.0.0.0', port=5000, threads=4)
