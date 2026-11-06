import os
import tempfile
import shutil
import unittest
from datetime import datetime, timezone, timedelta

os.environ["ECHOCHESS_ENV"] = "development"
os.environ["ECHOCHESS_DATA_DIR"] = tempfile.mkdtemp(prefix="echo-test-")

import auth
import invites
from store import save_json


class BetaSecurityTests(unittest.TestCase):
    def test_invalid_invite_different_length(self):
        result = auth.register_user("tester_a", "password12", "NOPE")
        self.assertEqual(result.get("error"), "Invalid invite code.")

    def test_invite_flow_limit_revoke_expire(self):
        created = invites.create_invite("admin", max_uses=1, days=14, label="one")
        code = created["code"]
        ok = auth.register_user("tester_b", "password12", code)
        self.assertIn("user", ok)
        again = auth.register_user("tester_c", "password12", code)
        self.assertEqual(again.get("error"), "This invite code has already been used.")

        created2 = invites.create_invite("admin", max_uses=2, days=14)
        invites.revoke_invite("admin", created2["id"])
        revoked = auth.register_user("tester_d", "password12", created2["code"])
        self.assertEqual(revoked.get("error"), "This invite code has been revoked.")

        created3 = invites.create_invite("admin", max_uses=1, days=14)
        invites_data = []
        from store import load_json
        for item in load_json("invites.json", []):
            if item["id"] == created3["id"]:
                item["expires_at"] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
            invites_data.append(item)
        save_json("invites.json", invites_data)
        expired = auth.register_user("tester_e", "password12", created3["code"])
        self.assertEqual(expired.get("error"), "This invite code has expired.")

    def test_admin_ban(self):
        auth.create_admin("rootadmin", "supersecret12")
        created = invites.create_invite("rootadmin", max_uses=1, days=14)
        auth.register_user("bannedguy", "password12", created["code"])
        result = auth.set_banned("rootadmin", "bannedguy", True)
        self.assertTrue(result["user"]["banned"])
        login = auth.login_user("bannedguy", "password12")
        self.assertIn("banned", login.get("error", "").lower())

    def test_profiles_preserved(self):
        self.assertTrue(os.path.exists("bot_profiles/deniz.json"))
        pgn_dir = os.path.join("users", "Mudur", "pgns")
        self.assertTrue(os.path.isdir(pgn_dir) or os.path.isdir("users/mudur/pgns"))


if __name__ == "__main__":
    unittest.main()
