import pytest

from app.identity.domain.exceptions.invalid_email_exception import (
    InvalidEmailException,
)
from app.identity.domain.value_objects.email import Email


class TestEmail:
    def test_create_email_with_valid_value(self):
        email = Email(value="test@example.com")
        assert email.value == "test@example.com"

    def test_create_email_normalizes_lowercase(self):
        email = Email(value="TEST@EXAMPLE.COM")
        assert email.value == "test@example.com"

    def test_create_email_strips_whitespace(self):
        email = Email(value="  test@example.com  ")
        assert email.value == "test@example.com"

    def test_create_email_raises_exception_for_missing_at_symbol(self):
        with pytest.raises(InvalidEmailException):
            Email(value="invalidemail")

    def test_create_email_raises_exception_for_empty_string(self):
        with pytest.raises(InvalidEmailException):
            Email(value="")

    def test_create_email_raises_exception_for_whitespace_only(self):
        with pytest.raises(InvalidEmailException):
            Email(value="   ")

    def test_email_str_representation(self):
        email = Email(value="test@example.com")
        assert str(email) == "test@example.com"

    def test_email_is_frozen(self):
        email = Email(value="test@example.com")
        with pytest.raises(AttributeError):
            email.value = "new@example.com"
