from app.identity.application.exceptions.account_already_exists_exception import (
    AccountAlreadyExistsException,
)
from app.identity.application.use_cases.signup.signup_input import SignupInput
from app.identity.application.use_cases.signup.signup_output import SignupOutput
from app.identity.domain.entities.account import Account
from app.identity.domain.value_objects.cpf import CPF
from app.identity.domain.value_objects.email import Email
from app.shared.application.unit_of_work import UnitOfWork


class Signup:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._unit_of_work = unit_of_work

    def execute(self, input_data: SignupInput) -> SignupOutput:
        with self._unit_of_work as uow:
            existing_by_tax_id = uow.account_repository.find_by_tax_id(
                CPF(input_data.tax_id)
            )

            if existing_by_tax_id:
                raise AccountAlreadyExistsException()

            existing_by_email = uow.account_repository.find_by_email(
                Email(input_data.email)
            )

            if existing_by_email:
                raise AccountAlreadyExistsException()

            account = Account.create(
                name=input_data.name,
                email=input_data.email,
                tax_id=input_data.tax_id,
            )

            uow.account_repository.save(account)
            uow.commit()

            return SignupOutput(
                account_id=account.id,
            )
