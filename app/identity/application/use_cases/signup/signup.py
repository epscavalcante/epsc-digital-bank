from app.identity.application.exceptions.account_already_exists_exception import (
    AccountAlreadyExistsException,
)
from app.identity.application.use_cases.signup.signup_input import SignupInput
from app.identity.application.use_cases.signup.signup_output import SignupOutput
from app.identity.domain.entities.account import Account
from app.identity.domain.repositories.account_repository import AccountRepository
from app.identity.domain.value_objects.cpf import CPF
from app.identity.domain.value_objects.email import Email


class Signup:
    def __init__(
        self,
        account_repository: AccountRepository,
    ) -> None:
        self.account_repository = account_repository

    def execute(self, input_data: SignupInput) -> SignupOutput:
        existing_by_tax_id = self.account_repository.find_by_tax_id(
            CPF(input_data.tax_id)
        )

        if existing_by_tax_id:
            raise AccountAlreadyExistsException()

        existing_by_email = self.account_repository.find_by_email(
            Email(input_data.email)
        )

        if existing_by_email:
            raise AccountAlreadyExistsException()

        account = Account.create(
            tax_id=input_data.tax_id,
            name=input_data.name,
            email=input_data.email,
        )

        self.account_repository.save(account)

        return SignupOutput(
            account_id=account.id,
        )
