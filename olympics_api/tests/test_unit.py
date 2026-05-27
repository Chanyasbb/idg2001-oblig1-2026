"""Unit tests for standalone helper functions — no server or DB needed."""

import uuid
import pytest
from app.utils.auth import hash_password, verify_password, generate_user_id
from app.utils.token_cost import COST_DEFAULT, COST_ATHLETE, COST_COUNTRY, COST_SPORT_QUERY


# auth helpers 

def test_generate_user_id_is_valid_uuid():
    """generate_user_id must return a valid UUID4 string."""
    uid = generate_user_id()
    parsed = uuid.UUID(uid)
    assert parsed.version == 4


def test_unique_user_ids():
    """Two consecutive IDs should never collide."""
    assert generate_user_id() != generate_user_id()


def test_hash_password_differs_from_plain():
    """Stored hash must not equal the original password."""
    assert hash_password("secret") != "secret"


def test_hash_password_produces_bcrypt_string():
    """bcrypt hashes always start with '$2b$'."""
    assert hash_password("abc").startswith("$2b$")


def test_verify_password_correct():
    """verify_password returns True for the matching password."""
    hashed = hash_password("my_password")
    assert verify_password("my_password", hashed) is True


def test_verify_password_wrong():
    """verify_password returns False for a non-matching password."""
    hashed = hash_password("my_password")
    assert verify_password("wrong", hashed) is False


def test_same_password_different_hashes():
    """bcrypt uses random salts — two hashes of the same password differ."""
    assert hash_password("abc") != hash_password("abc")


#  token costs 

@pytest.mark.parametrize("cost", [COST_DEFAULT, COST_ATHLETE, COST_COUNTRY, COST_SPORT_QUERY])
def test_token_costs_are_positive(cost):
    """All token cost constants must be at least 1."""
    assert cost >= 1
