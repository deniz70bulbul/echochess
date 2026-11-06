import hashlib
import secrets
from datetime import datetime, timezone, timedelta

from store import load_json, save_json, locked, utc_now, append_audit

INVITES_FILE = "invites.json"


def _hash_code(code: str) -> str:
    normalized = (code or "").strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _parse_dt(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@locked
def list_invites():
    invites = load_json(INVITES_FILE, [])
    public = []
    for item in invites:
        public.append({
            "id": item["id"],
            "label": item.get("label") or "",
            "max_uses": item.get("max_uses", 1),
            "used_count": item.get("used_count", 0),
            "revoked": bool(item.get("revoked")),
            "expires_at": item.get("expires_at"),
            "created_at": item.get("created_at"),
            "used_by": item.get("used_by", []),
        })
    return public


@locked
def create_invite(actor, max_uses=1, days=14, label=""):
    max_uses = max(1, int(max_uses or 1))
    days = max(1, int(days or 14))
    code = "EC-" + secrets.token_urlsafe(18)
    invite = {
        "id": secrets.token_hex(8),
        "code_hash": _hash_code(code),
        "label": (label or "").strip()[:80],
        "max_uses": max_uses,
        "used_count": 0,
        "used_by": [],
        "revoked": False,
        "created_at": utc_now(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=days)).isoformat(),
    }
    invites = load_json(INVITES_FILE, [])
    invites.append(invite)
    save_json(INVITES_FILE, invites)
    append_audit("invite.create", actor, {"id": invite["id"], "max_uses": max_uses})
    return {"id": invite["id"], "code": code, "expires_at": invite["expires_at"], "max_uses": max_uses}


@locked
def revoke_invite(actor, invite_id):
    invites = load_json(INVITES_FILE, [])
    found = False
    for item in invites:
        if item["id"] == invite_id:
            item["revoked"] = True
            found = True
            break
    if not found:
        return {"error": "Invite not found."}
    save_json(INVITES_FILE, invites)
    append_audit("invite.revoke", actor, {"id": invite_id})
    return {"status": "revoked"}


def consume_invite(code, username):
    return _consume(code, username)


@locked
def _consume(code, username):
    raw = (code or "").strip()
    if not raw:
        return {"error": "Invite code is required."}

    code_hash = _hash_code(raw)
    invites = load_json(INVITES_FILE, [])
    now = datetime.now(timezone.utc)
    matched = None

    for item in invites:
        stored = item.get("code_hash") or ""
        if len(stored) == len(code_hash) and secrets.compare_digest(stored, code_hash):
            matched = item
            break

    if matched is None:
        return {"error": "Invalid invite code."}

    if matched.get("revoked"):
        return {"error": "This invite code has been revoked."}

    expires = _parse_dt(matched.get("expires_at"))
    if expires is not None and now > expires:
        return {"error": "This invite code has expired."}

    used = int(matched.get("used_count") or 0)
    max_uses = int(matched.get("max_uses") or 1)
    if used >= max_uses:
        return {"error": "This invite code has already been used."}

    matched["used_count"] = used + 1
    used_by = matched.setdefault("used_by", [])
    used_by.append({"username": username, "at": utc_now()})
    save_json(INVITES_FILE, invites)
    return {"ok": True, "id": matched["id"]}
