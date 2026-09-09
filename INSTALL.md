# Park View Drugs — Server Installation Guide

Flask + SQLite pharmacy website, served by Waitress on port 5050 over Tailscale.
This guide is for installing on a NEW server (Windows or Linux).

---

## What's in this package

```
app.py                  Flask application (routes, admin CRUD, DB helpers)
run_prod.py             Production entry (Waitress, binds loopback + Tailscale IP)
requirements.txt        Python dependencies
database/schema.sql     SQLite schema + seed data
static/                 CSS, JS, images
templates/              Jinja2 templates (public + admin)
instance/parkview.db    Optional: existing data (services, deals, products, settings)
.env.example            Environment variable reference
setup_env.ps1           [Windows] Generate fresh secret key + admin password hash
install_service.ps1     [Windows] Register boot-persistent scheduled task
install_task.ps1        [Windows] Alternative task installer
start_server.bat        [Windows] Task launcher (location-agnostic)
start_hidden.vbs        [Windows] Silent startup launcher (optional)
check_firewall.ps1      [Windows] Firewall diagnostics
README.md               Full project documentation
```

---

## Windows installation (recommended)

### Prerequisites
- Windows 10/11, Python 3.11+ installed (or `py -3.11`)
- Tailscale installed and signed in to your tailnet (`wecaregd2026@`)
- Administrator access

### Steps

1. **Copy the package** to the target server, e.g. `C:\ParkViewWeb` (any path works —
   all scripts resolve their own location).

2. **Create the virtual environment and install dependencies** (from the app folder):
   ```bat
   py -3.11 -m venv .venv
   .venv\Scripts\python.exe -m pip install --upgrade pip
   .venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. **Verify Tailscale IP** (used for the bind):
   ```bat
   tailscale ip -4
   ```
   `run_prod.py` auto-detects this at startup; no config needed.

4. **Set credentials** — right-click PowerShell > Run as Administrator, then:
   ```powershell
   cd C:\ParkViewWeb
   .\setup_env.ps1
   ```
   Enter an admin password (min 8 chars). This generates a fresh
   `PARKVIEW_SECRET_KEY` and `PARKVIEW_ADMIN_PASSWORD_HASH` as
   **machine-level** env vars (the SYSTEM task needs them there).

5. **Register the persistent service** (same admin PowerShell):
   ```powershell
   .\install_service.ps1
   ```
   This creates the `ParkViewDrugsServer` scheduled task: starts at boot as
   SYSTEM, restarts up to 3 times on failure.

6. **Open the firewall for Tailscale only** (admin PowerShell):
   ```powershell
   New-NetFirewallRule -DisplayName 'ParkViewDrugs-Tailscale' -Direction Inbound -Action Allow -Protocol TCP -LocalPort 5050 -InterfaceAlias 'Tailscale'
   ```

7. **Verify**:
   ```bat
   curl http://127.0.0.1:5050/healthz      :: expect {"status":"ok",...}
   curl http://127.0.0.1:5050/             :: expect 200
   curl http://<tailscale-ip>:5050/        :: expect 200
   ```
   Open `http://<tailscale-ip>:5050/admin/login` in a browser and log in with the
   password you set in step 4.

> **Dependencies are verified automatically**: `install_service.ps1` runs
> `pip install -r requirements.txt` (idempotent) and verifies `flask` +
> `waitress` import cleanly BEFORE registering the task — a broken environment
> fails fast with a clear message instead of a server that dies at boot.
> It also creates the Tailscale firewall rule and a daily database backup task
> (see Backups), and the server task runs with **no execution time limit**
> (the default 72-hour cap would otherwise silently kill the site every 3 days).

> **First run:** `run_prod.py` initializes the SQLite database automatically from
> `database/schema.sql`. If you ship `instance/parkview.db` (existing data) it is
> used as-is; delete it to start from seed data.

---

## Linux installation (Ubuntu/Debian)

```bash
# 1. Copy the package to e.g. /opt/parkview and enter it
cd /opt/parkview

# 2. Python env
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt

# 3. Credentials - set as environment variables for the service
export PARKVIEW_SECRET_KEY="$(openssl rand -hex 32)"
export PARKVIEW_ADMIN_PASSWORD_HASH="$(.venv/bin/python -c 'from werkzeug.security import generate_password_hash; print(generate_password_hash("your-password"))')"

# 4. Tailscale must be up so run_prod.py can detect its IP
tailscale up

# 5. Run (foreground test)
.venv/bin/python run_prod.py

# 6. Install as a systemd service
sudo tee /etc/systemd/system/parkview.service >/dev/null <<'EOF'
[Unit]
Description=Park View Drugs web app
After=network-online.target tailscaled.service
Wants=network-online.target

[Service]
WorkingDirectory=/opt/parkview
EnvironmentFile=/etc/parkview.env
ExecStart=/opt/parkview/.venv/bin/python /opt/parkview/run_prod.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Environment file (chmod 600!)
cat > /etc/parkview.env <<EOF
PARKVIEW_SECRET_KEY=your-generated-secret
PARKVIEW_ADMIN_PASSWORD_HASH=your-generated-hash
EOF
sudo chmod 600 /etc/parkview.env

sudo systemctl daemon-reload
sudo systemctl enable --now parkview
```

Firewall note: `run_prod.py` binds only 127.0.0.1 + the Tailscale IP, so
no host firewall rule is needed for LAN exposure — Tailscale traffic is
permitted by the tailnet policy.

---

## Security notes

- **Never ship `PARKVIEW_ADMIN_PASSWORD_HASH`/`PARKVIEW_SECRET_KEY` values in the
  package or in git.** Always generate fresh ones per server (`setup_env.ps1` /
  Linux env file).
- The production server binds loopback + Tailscale only — it is NOT exposed on
  the LAN. Verify with `netstat -ano | findstr :5050` (Windows) — you should see
  only `127.0.0.1:5050` and your `100.x.y.z:5050`.
- Admin session cookie is HttpOnly + SameSite=Lax. Set `PARKVIEW_COOKIE_SECURE=true`
  only behind HTTPS (e.g. Cloudflare Tunnel or Tailscale Serve with HTTPS).

---

## Backups

The entire site data lives in one file: `instance/parkview.db`.
`install_service.ps1` registers a **daily backup task** (`ParkViewDrugsBackup`,
03:00) that copies it to `backup\parkview-<timestamp>.db` and keeps the newest
14 copies. Run `.\backup_db.ps1` manually at any time.

---

## Updating

Replace the app files, keep `.venv` and `instance/`. Restart the task:
```powershell
Restart-ScheduledTask -TaskName 'ParkViewDrugsServer'
```
