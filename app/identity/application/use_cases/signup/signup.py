from app.banking.domain.entities.wallet import Wallet
from app.banking.domain.repositories.wallet_repository import WalletRepository
from app.identity.application.exceptions.account_already_exists_exception import (
    AccountAlreadyExistsException,
)
from app.identity.application.use_cases.signup.signup_input import SignupInput
from app.identity.application.use_cases.signup.signup_output import SignupOutput
from app.identity.domain.entities.account import Account
from app.identity.domain.repositories.account_repository import AccountRepository
from app.identity.domain.value_objects.cpf import CPF
from app.identity.domain.value_objects.email import Email
from app.shared.application.unit_of_work import UnitOfWork


class Signup:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        account_repository: AccountRepository,
        wallet_repository: WalletRepository,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._account_repository = account_repository
        self._wallet_repository = wallet_repository

    def execute(self, input_data: SignupInput) -> SignupOutput:
        with self._unit_of_work as uow:
            existing_by_tax_id = self._account_repository.find_by_tax_id(
                CPF(input_data.tax_id)
            )

            if existing_by_tax_id:
                raise AccountAlreadyExistsException()

            existing_by_email = self._account_repository.find_by_email(
                Email(input_data.email)
            )

            if existing_by_email:
                raise AccountAlreadyExistsException()

            account = Account.create(
                name=input_data.name,
                email=input_data.email,
                tax_id=input_data.tax_id,
            )
            # fazer a criação por evento...
            wallet = Wallet.create(account_id=account.id)

            self._account_repository.save(account)
            self._wallet_repository.save(wallet)
            uow.commit()

            return SignupOutput(
                account_id=account.id,
            )
