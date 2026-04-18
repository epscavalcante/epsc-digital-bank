import pytest

from app.identity.domain.exceptions.invalid_name_exception import InvalidNameException
from app.identity.domain.value_objects.name import Name


class TestName:
    def test_create_name_with_valid_value(self):
        name = Name(value="John Doe")
        assert name.value == "John Doe"

    def test_create_name_strips_whitespace(self):
        name = Name(value="  John Doe  ")
        assert name.value == "John Doe"

    def test_create_name_raises_exception_for_empty_string(self):
        with pytest.raises(InvalidNameException):
            Name(value="")

    def test_create_name_raises_exception_for_whitespace_only(self):
        with pytest.raises(InvalidNameException):
            Name(value="   ")

    def test_name_str_representation(self):
        name = Name(value="John Doe")
        assert str(name) == "John Doe"

    def test_name_is_frozen(self):
        name = Name(value="John Doe")
        with pytest.raises(AttributeError):
            name.value = "Jane Doe"

    def test_create_name_with_single_word(self):
        name = Name(value="John")
        assert name.value == "John"

    def test_create_name_with_special_characters(self):
        name = Name(value="José da Silva")
        assert name.value == "José da Silva"
