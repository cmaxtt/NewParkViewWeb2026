# Cloudflare + Tailscale Hosting Implementation Plan

## Recommendation

Use a hybrid setup:

- **Cloudflare Tunnel** for the public customer website.
- **Tailscale** for private administrator access.
- Keep the Flask application hosted on this Windows computer.
- Do not forward ports on the home/office router.

Public customer URL:

```text
https://shop.<your-domain>
```

Private administrator access:

```text
http://127.0.0.1:5050/admin/login
```

or through a private Tailscale hostname after Tailscale Serve is configured.

## Current Project State

- Flask application entry point: `app.py`
- Production entry point: `run_prod.py`
- Production server: Waitress
- Current application port: `5050`
- Current scheduled launcher: `start_server.bat`
- Existing Windows scheduled-task installers:
  - `install_service.ps1`
  - `install_task.ps1`
- Existing private-network documentation uses Tailscale.
- Cloudflare Tunnel is not currently configured in this repository.

## Target Architecture

```text
Customers
    |
    | HTTPS
    v
Cloudflare DNS + Cloudflare Tunnel
    |
    | local tunnel connection
    v
127.0.0.1:5050
    |
    v
Waitress -> Flask application -> SQLite database

Administrator
    |
    v
Tailscale private network / Tailscale Serve
    |
    v
127.0.0.1:5050/admin/login
```

The application should listen only on `127.0.0.1` once the tunnel and private proxy are working. This prevents direct access from the local LAN and leaves Cloudflare/Tailscale as the controlled entry points.

## Required Application Changes

Before exposing the site publicly:

1. Change the Waitress bind address in `run_prod.py` from `0.0.0.0` to `127.0.0.1`.
2. Install and verify the pinned `waitress` dependency from `requirements.txt`.
3. Set a persistent random `PARKVIEW_SECRET_KEY`.
4. Store the admin password as a Werkzeug hash in `PARKVIEW_ADMIN_PASSWORD_HASH`.
5. Remove the plaintext fallback admin password from production configuration.
6. Set `PARKVIEW_COOKIE_SECURE=true` for HTTPS access.
7. Run the production entry point with debug mode disabled.
8. Keep the SQLite database and generated product images on the local machine; do not expose the database directory through the web server.

The current development fallback password should not be used once the site is public.

## Cloudflare Setup

### Prerequisites

- A domain already managed by Cloudflare.
- The desired hostname, recommended as `shop.<your-domain>`.
- Cloudflare account access with permission to create a Tunnel and DNS record.
- `cloudflared` installed on the Windows host.

### Configuration Steps

1. Install `cloudflared` on the Windows host.
2. Authenticate it with the Cloudflare account.
3. Create a named tunnel, for example `parkview-drugs`.
4. Configure the tunnel origin as:

   ```text
   http://127.0.0.1:5050
   ```

5. Route `shop.<your-domain>` to the tunnel.
6. Confirm Cloudflare issues HTTPS for the hostname.
7. Install the tunnel as a Windows service or scheduled task.
8. Configure automatic restart after failure.

Example tunnel configuration shape:

```yaml
tunnel: <tunnel-id>
credentials-file: C:\\Users\\<windows-user>\\.cloudflared\\<tunnel-id>.json

ingress:
  - hostname: shop.<your-domain>
    service: http://127.0.0.1:5050
  - service: http_status:404
```

The tunnel credentials file must be readable only by the service account that runs `cloudflared`.

## Tailscale Setup

Use Tailscale for private administration and maintenance.

1. Keep Tailscale installed and signed in on the server computer.
2. Confirm the administrator devices belong to the same tailnet.
3. Use Tailscale Serve to proxy a private HTTPS endpoint to `127.0.0.1:5050`, or use an equivalent private Tailscale route.
4. Restrict access through the Tailscale ACL policy to administrator devices or users.
5. Use the private Tailscale address for `/admin/login` and maintenance work.

Do not rely on the public customer hostname as the only protection for the admin area. Add Cloudflare Access for `/admin/*` as a second layer if administrators must use the public hostname.

## Windows Startup and Recovery

Create or update two persistent services/tasks:

### Park View Drugs application

- Starts `start_server.bat` at system startup.
- Runs `.venv\Scripts\python.exe run_prod.py`.
- Writes to `server.log`.
- Restarts after failure.

### Cloudflare Tunnel

- Starts `cloudflared tunnel run parkview-drugs` at system startup.
- Uses the named tunnel credentials.
- Restarts after failure.
- Writes a separate tunnel log.

Start the Flask service before the tunnel, or configure the tunnel service to retry until port `5050` is available.

## Security Checklist

- [ ] Use a password hash, not plaintext admin credentials.
- [ ] Set a persistent random Flask secret key.
- [ ] Disable Flask debug mode.
- [ ] Enable secure session cookies.
- [ ] Bind the origin to `127.0.0.1`.
- [ ] Do not open router port `5050`.
- [ ] Restrict Tailscale access with ACLs.
- [ ] Protect admin access with Tailscale and/or Cloudflare Access.
- [ ] Keep tunnel credentials outside the repository.
- [ ] Do not commit `.env`, tunnel credentials, SQLite files, or logs.
- [ ] Back up `instance\parkview.db` separately.
- [ ] Keep the operating system, Python dependencies, Tailscale, and `cloudflared` updated.

## Verification Checklist

### Local origin

- `http://127.0.0.1:5050/` returns HTTP 200.
- `/products?category=Vitamins` returns the product listing.
- Product images return HTTP 200.
- Admin login accepts the configured password hash.

### Cloudflare public access

- `https://shop.<your-domain>/` loads successfully.
- HTTPS certificate is valid.
- Product pages, search, images, forms, and static assets work.
- The public hostname does not expose server files or the SQLite database.
- The site continues working after restarting the Flask process.

### Tailscale private access

- Administrator can reach the private hostname.
- Unauthorized tailnet devices cannot reach the admin endpoint.
- Admin login remains protected by the application password.

### Restart test

- Restart Windows.
- Confirm the Flask service starts.
- Confirm the Cloudflare Tunnel starts.
- Confirm the public URL becomes available without manual terminal commands.

## Rollout Order

1. Fix production dependency and configuration issues.
2. Generate and install production secrets.
3. Change the origin binding to localhost.
4. Test the production Waitress server locally.
5. Configure and test Tailscale private administration.
6. Install and test Cloudflare Tunnel with a temporary hostname or staging subdomain.
7. Configure `shop.<your-domain>`.
8. Run the restart and security verification checks.
9. Publish the public URL to customers.

## Decision Summary

For this project, use **Cloudflare Tunnel for public customer access** and **Tailscale for private administration**. Tailscale alone is excellent for private sharing but is not suitable as the primary customer-facing hosting method. Cloudflare Tunnel provides the public HTTPS hostname without opening inbound router ports, while Tailscale keeps administration private.
