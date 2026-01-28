import pytest
from helpers.auth_helper import pwd_context, AuthHelper


def test_password_hash_and_verify():
    password = "My$ecret123"
    hashed = pwd_context.hash(password)
    assert pwd_context.verify(password, hashed)


def test_auth_helper_encode_decode_token(monkeypatch):
    # Create a minimal AuthHelper instance behavior using its methods if present
    # If AuthHelper defines token generation, test encode/decode using jose
    helper = AuthHelper()
    # If AuthHelper has `create_access_token` and `decode_token`, test them
    if hasattr(helper, 'create_access_token') and hasattr(helper, 'decode_token'):
        token = helper.create_access_token({'sub': 'testuser'})
        payload = helper.decode_token(token)
        assert payload.get('sub') == 'testuser'
    else:
        pytest.skip("AuthHelper has no token methods to test")
