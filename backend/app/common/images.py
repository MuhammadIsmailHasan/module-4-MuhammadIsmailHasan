"""Avatar image detection from the leading bytes only (V10, Decision R)."""
MAX_AVATAR_BYTES = 2_097_152
AVATAR_TYPES = {"png": "image/png", "jpg": "image/jpeg", "webp": "image/webp"}


def detect_image_type(head):
    """"png", "jpg", "webp" or None. The file name and the declared Content-Type are never consulted."""
    if head[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if head[:3] == b"\xff\xd8\xff":
        return "jpg"
    if len(head) >= 12 and head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    return None
