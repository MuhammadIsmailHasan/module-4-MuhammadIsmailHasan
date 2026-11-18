import hashlib
import hmac

from flask import current_app

TTL_SECONDS = 900


def _secret(secret):
    return (secret or current_app.config["FILE_URL_SECRET"]).encode()


def _mac(attachment_id, exp, secret):
    return hmac.new(_secret(secret), f"{attachment_id}.{exp}".encode(), hashlib.sha256).hexdigest()


def sign_file_url(attachment_id, now, secret=None):
    exp = int(now.timestamp()) + TTL_SECONDS
    return f"/api/attachments/{attachment_id}/file?exp={exp}&sig={_mac(attachment_id, exp, secret)}", exp


def verify_file_signature(attachment_id, exp, sig, now, secret=None):
    if not exp or not sig:
        return False
    try:
        exp_i = int(exp)
    except (TypeError, ValueError):
        return False
    if not hmac.compare_digest(_mac(attachment_id, exp_i, secret), str(sig)):
        return False
    return int(now.timestamp()) <= exp_i
