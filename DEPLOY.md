# EchoChess global beta deploy

Do not buy paid plans or go live until the owner approves.

## Architecture (single region, global CDN)

- **Frontend:** Cloudflare Pages (global CDN). Build `frontend/` with `VITE_API_URL=https://<api-host>`.
- **Backend:** Render or Railway Python web service, bind `0.0.0.0:$PORT`.
- **Data:** persistent disk on the API host (`ECHOCHESS_DATA_DIR`) for `users.json`, invites, sessions, `bot_profiles/`, `users/*/pgns/`.
- One region (EU recommended: Frankfurt/Amsterdam) keeps chess analysis and PGN files close to the API. Add more regions later only if latency requires it.

## Free publish (Europe + Turkey, $0)

One Render **Free** Docker service in **Frankfurt**. UI and API share the same HTTPS URL (no Cloudflare, no domain, no disk).

Turkey and Europe hit the Frankfurt region. First request after idle is slow (free sleep).

**Data on this plan is throwaway.** Local `deniz` / PGN stay on your PC and are not uploaded.

Dashboard: New Web Service → Docker → region Frankfurt → instance Free.

## Environment

API:

```
ECHOCHESS_ENV=production
ECHOCHESS_SECRET_KEY=<long random>
ECHOCHESS_FRONTEND_ORIGINS=https://echochess.pages.dev
ECHOCHESS_COOKIE_SECURE=true
ECHOCHESS_COOKIE_SAMESITE=none
ECHOCHESS_DATA_DIR=/var/data
```

Frontend build:

```
VITE_API_URL=https://echochess-api.onrender.com
```

Copy existing `users.json`, `bot_profiles/`, and `users/` onto the disk before first start.

## HTTPS / domain

Point the API hostname to the Python service and the site hostname to Pages. TLS is terminated by the host. Enable HTTPS in the dashboard; do not rely on app-level HTTP redirects (they break health checks).

## Admin bootstrap (server shell only)

```
python bootstrap_admin.py --username <admin> --password <long-password>
```

Then log in and create invite codes from `/admin`. Raw codes are shown once.

## Backup

```
python backup.py
```

Copies accounts, invites, profiles, and PGNs to `backups/<timestamp>/`.

## Owner steps still required

1. Create Cloudflare Pages + Render/Railway accounts.
2. Add a persistent disk.
3. Set the env vars above.
4. Create the admin with `bootstrap_admin.py`.
5. Confirm domain DNS and HTTPS.
6. Explicitly approve going live.
