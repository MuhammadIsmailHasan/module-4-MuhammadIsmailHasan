from datetime import datetime, timedelta, timezone

from hypothesis import given, strategies as st

from app.common import ordering
from app.common.signing import sign_file_url, verify_file_signature

NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
SECRET = "s" * 32


def _parts(url):
    q = url.split("?")[1]
    d = dict(p.split("=") for p in q.split("&"))
    return d["exp"], d["sig"]


@given(st.lists(st.floats(-1e6, 1e6), unique=True, min_size=2, max_size=20))
def test_position_between_neighbours(orders):
    orders.sort()
    prev, nxt = orders[0], orders[-1]
    pos = ordering.position_for(prev, nxt, orders)
    assert prev <= pos <= nxt


def test_position_edges():
    assert ordering.position_for(None, None, []) == 1.0
    assert ordering.position_for(None, 3.0, [3.0, 5.0]) == 2.0
    assert ordering.position_for(5.0, None, [3.0, 5.0]) == 6.0


def test_rebalance_and_trigger():
    assert ordering.needs_rebalance(1.0, 1.0 + 1e-7)
    assert not ordering.needs_rebalance(1.0, 2.0)
    assert ordering.rebalance([0.5, 0.5000001, 9]) == [1.0, 2.0, 3.0]


def test_signed_url_valid_expired_tampered():
    path, _ = sign_file_url("abc", NOW, SECRET)
    exp, sig = _parts(path)
    assert verify_file_signature("abc", exp, sig, NOW, SECRET)
    assert verify_file_signature("abc", exp, sig, NOW + timedelta(seconds=900), SECRET)
    assert not verify_file_signature("abc", exp, sig, NOW + timedelta(seconds=901), SECRET)
    assert not verify_file_signature("abc", exp, sig + "0", NOW, SECRET)
    assert not verify_file_signature("abc", str(int(exp) + 1), sig, NOW, SECRET)
    assert not verify_file_signature("abd", exp, sig, NOW, SECRET)
    assert not verify_file_signature("abc", None, None, NOW, SECRET)
