import pytest

from app.identity.domain.exceptions.invalid_cpf_exception import InvalidCPFException
from app.identity.domain.value_objects.cpf import CPF


class TestCPF:
    # CPFs válidos para testes
    VALID_CPF_1 = "52998224725"  # CPF válido real
    VALID_CPF_2 = "11144477735"  # CPF válido real

    def test_create_cpf_with_valid_value(self):
        cpf = CPF(value=self.VALID_CPF_1)
        assert cpf.value == self.VALID_CPF_1

    def test_create_cpf_removes_non_digits(self):
        cpf = CPF(value="529.982.247-25")
        assert cpf.value == self.VALID_CPF_1

    def test_create_cpf_raises_exception_for_less_than_11_digits(self):
        with pytest.raises(InvalidCPFException) as exc_info:
            CPF(value="123456789")
        assert "11 dígitos" in str(exc_info.value)

    def test_create_cpf_raises_exception_for_more_than_11_digits(self):
        with pytest.raises(InvalidCPFException) as exc_info:
            CPF(value="1234567890123")
        assert "11 dígitos" in str(exc_info.value)

    def test_create_cpf_raises_exception_for_all_same_digits(self):
        with pytest.raises(InvalidCPFException) as exc_info:
            CPF(value="11111111111")
        assert "Padrão inválido" in str(exc_info.value)

    def test_create_cpf_raises_exception_for_invalid_check_digits(self):
        # CPF válido mas com dígitos verificadores alterados
        with pytest.raises(InvalidCPFException) as exc_info:
            CPF(value="52998224700")
        assert "Dígitos verificadores inválidos" in str(exc_info.value)

    def test_cpf_value_property(self):
        cpf = CPF(value=self.VALID_CPF_1)
        assert cpf.value == self.VALID_CPF_1

    def test_cpf_repr(self):
        cpf = CPF(value=self.VALID_CPF_1)
        assert repr(cpf) == f"CPF(value='{self.VALID_CPF_1}')"

    def test_cpf_is_frozen(self):
        cpf = CPF(value=self.VALID_CPF_1)
        with pytest.raises(AttributeError):
            cpf.value = "00000000000"

    def test_create_cpf_with_valid_real_cpf(self):
        cpf = CPF(value=self.VALID_CPF_2)
        assert cpf.value == self.VALID_CPF_2

    def test_create_cpf_with_spaces(self):
        cpf = CPF(value=f"  {self.VALID_CPF_1}  ")
        assert cpf.value == self.VALID_CPF_1
