"""Avatar upload, signed URLs and removal (Requirement 19, criteria 18 to 27; Property 47)."""
import io
import os

from hypothesis import given, strategies as st

from conftest import TEST_PASSWORD
from helpers import PROP
from app.common.images import MAX_AVATAR_BYTES, detect_image_type

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32
JPG = b"\xff\xd8\xff\xe0" + b"0" * 32
WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"0" * 32


def _up(client, h, data, name="a.png", mime="image/png"):
    return client.post("/api/users/me/avatar", headers=h, data={"file": (io.BytesIO(data), name, mime)}, content_type="multipart/form-data")


@PROP
@given(head=st.binary(max_size=40))
def test_property_47_detect_image_type_only_from_bytes(head):
    kind = detect_image_type(head)
    expected = (
        "png" if head[:8] == b"\x89PNG\r\n\x1a\n" else "jpg" if head[:3] == b"\xff\xd8\xff" else "webp" if head[:4] == b"RIFF" and head[8:12] == b"WEBP" else None
    )
    assert kind == expected


def test_avatar_upload_replace_remove_and_signed_file(app, client, make_user, auth):
    user = make_user("member", "pic")
    h = auth(user)
    assert client.post("/api/users/me/avatar").status_code == 401
    assert client.delete("/api/users/me/avatar").status_code == 401
    assert client.get("/api/auth/me", headers=h).get_json()["data"]["avatar_url"] is None

    first = _up(client, h, PNG, name="../evil.exe", mime="text/plain")  # name and type are ignored
    assert first.status_code == 200 and first.get_json()["message"] == "Avatar updated"
    url = first.get_json()["data"]["avatar_url"]
    assert url.startswith(f"/api/users/{user.id}/avatar/file?exp=")
    avatars = os.path.join(app.config["UPLOAD_DIR"], "avatars")
    stored = os.listdir(avatars)
    assert len(stored) == 1 and stored[0].endswith(".png") and "evil" not in stored[0]

    file = client.get(url)
    assert file.status_code == 200 and file.mimetype == "image/png" and file.data == PNG
    assert file.headers["X-Content-Type-Options"] == "nosniff" and file.headers["Content-Disposition"] == "inline"
    assert file.headers["Cache-Control"] == "private, max-age=300"
    assert client.get(url.replace("sig=", "sig=0")).status_code == 403
    assert client.get(f"/api/users/{user.id}/avatar/file").status_code == 403

    second = _up(client, h, JPG, name="x", mime="application/pdf")
    assert second.status_code == 200
    assert [f.rsplit(".", 1)[1] for f in os.listdir(avatars)] == ["jpg"]  # exactly one file remains
    assert _up(client, h, WEBP).status_code == 200

    gone = client.delete("/api/users/me/avatar", headers=h)
    assert gone.get_json()["message"] == "Avatar removed" and gone.get_json()["data"]["avatar_url"] is None
    assert os.listdir(avatars) == []
    assert client.delete("/api/users/me/avatar", headers=h).status_code == 200
    assert client.get(url).status_code == 403 or client.get(url).status_code == 404

    from app.models import ActivityLog

    rows = [a for a in ActivityLog.query.all() if a.action == "user.profile_updated"]
    assert rows and all(r.metadata_ == {"fields": ["avatar"]} for r in rows)


def test_avatar_rejections(app, client, make_user, auth):
    h = auth(make_user("member", "rej"))
    for data, name in ((b"hello world", "a.png"), (b"<svg xmlns='x'/>", "a.svg"), (b"GIF89a" + b"0" * 20, "a.gif"), (b"", "a.png")):
        r = _up(client, h, data, name=name)
        assert r.status_code == 400 and "file" in r.get_json()["error"]["details"], name
    assert _up(client, h, PNG + b"0" * (MAX_AVATAR_BYTES - len(PNG) + 1)).status_code == 400
    assert _up(client, h, PNG + b"0" * (MAX_AVATAR_BYTES - len(PNG))).status_code == 200  # exactly 2 MiB
    assert client.post("/api/users/me/avatar", headers=h, data={}, content_type="multipart/form-data").status_code == 400
    assert client.patch("/api/auth/me", headers=h, json={"full_name": "x", "avatar_url": "https://x.y/z.png"}).status_code == 400


def test_avatar_signature_never_opens_an_attachment_and_admin_cannot_set_url(client, make_user, auth):
    admin = make_user("admin", "boss")
    other = make_user("member", "other1")
    h = auth(other)
    url = _up(client, h, PNG).get_json()["data"]["avatar_url"]
    exp_sig = url.split("?", 1)[1]
    assert client.get(f"/api/attachments/{other.id}/file?{exp_sig}").status_code == 403
    ha = auth(admin)
    assert client.patch(f"/api/users/{other.id}", headers=ha, json={"avatar_url": "https://x.y"}).status_code == 400
    assert client.post("/api/users", headers=ha, json={"full_name": "N", "username": "newbie", "email": "n@x.com", "password": TEST_PASSWORD, "avatar_url": "https://x.y"}).status_code == 400
    listing = client.get("/api/users", headers=ha).get_json()["data"]
    assert any(u["avatar_url"] for u in listing)
