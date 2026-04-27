from uuid import UUID

from fastapi.testclient import TestClient

from app.shared.infrastructure.sqlalchemy_unit_of_work import SqlAlchemyUnitOfWork
from app.main import create_app


class TestApi:
    @staticmethod
    def _get_wallet_id(app, account_id: str) -> str | None:
        with SqlAlchemyUnitOfWork(app.state.database) as uow:
            wallet = uow.wallet_repository.find_by_account_id(UUID(account_id))
            return str(wallet.id) if wallet is not None else None

    def test_healthcheck_returns_ok(self, tmp_path):
        database_url = f"sqlite:///{tmp_path / 'test.db'}"
        app = create_app(database_url=database_url)

        with TestClient(app) as client:
            response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_signup_creates_account(self, tmp_path):
        database_url = f"sqlite:///{tmp_path / 'test.db'}"
        app = create_app(database_url=database_url)

        with TestClient(app) as client:
            response = client.post(
                "/accounts",
                json={
                    "tax_id": "52998224725",
                    "name": "John Doe",
                    "email": "john@example.com",
                },
            )

        assert response.status_code == 201
        assert "account_id" in response.json()

    def test_signup_returns_conflict_for_existing_account(self, tmp_path):
        database_url = f"sqlite:///{tmp_path / 'test.db'}"
        app = create_app(database_url=database_url)

        with TestClient(app) as client:
            first_response = client.post(
                "/accounts",
                json={
                    "tax_id": "52998224725",
                    "name": "John Doe",
                    "email": "john@example.com",
                },
            )
            second_response = client.post(
                "/accounts",
                json={
                    "tax_id": "52998224725",
                    "name": "John Doe",
                    "email": "john@example.com",
                },
            )

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert second_response.json() == {"detail": "Account already exists"}

    def test_deposit_persists_transaction(self, tmp_path):
        database_url = f"sqlite:///{tmp_path / 'test.db'}"
        app = create_app(database_url=database_url)

        with TestClient(app) as client:
            signup_response = client.post(
                "/accounts",
                json={
                    "tax_id": "52998224725",
                    "name": "John Doe",
                    "email": "john@example.com",
                },
            )
            account_id = signup_response.json()["account_id"]
            wallet_id = self._get_wallet_id(app, account_id)

            deposit_response = client.post(
                f"/wallets/{wallet_id}/deposits",
                json={
                    "amount": "100.00",
                },
                headers={"Idempotency-Key": "deposit-api-001"},
            )

        assert deposit_response.status_code == 201
        assert wallet_id is not None
        assert deposit_response.json() == {
            "transaction_id": deposit_response.json()["transaction_id"],
            "wallet_id": wallet_id,
            "amount": {
                "amount": "100.00",
                "currency": "BRL",
            },
            "transaction_type": "deposit",
            "status": "completed",
        }

    def test_deposit_returns_not_found_for_unknown_wallet(self, tmp_path):
        database_url = f"sqlite:///{tmp_path / 'test.db'}"
        app = create_app(database_url=database_url)

        with TestClient(app) as client:
            response = client.post(
                "/wallets/123e4567-e89b-12d3-a456-426614174000/deposits",
                json={
                    "amount": "100.00",
                },
                headers={"Idempotency-Key": "deposit-api-404"},
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Account not found"}

    def test_deposit_requires_idempotency_key_header(self, tmp_path):
        database_url = f"sqlite:///{tmp_path / 'test.db'}"
        app = create_app(database_url=database_url)

        with TestClient(app) as client:
            signup_response = client.post(
                "/accounts",
                json={
                    "tax_id": "52998224725",
                    "name": "John Doe",
                    "email": "john@example.com",
                },
            )
            account_id = signup_response.json()["account_id"]
            wallet_id = self._get_wallet_id(app, account_id)

            response = client.post(
                f"/wallets/{wallet_id}/deposits",
                json={
                    "amount": "100.00",
                },
            )

        assert wallet_id is not None
        assert response.status_code == 422

    def test_transfer_persists_transaction(self, tmp_path):
        database_url = f"sqlite:///{tmp_path / 'test.db'}"
        app = create_app(database_url=database_url)

        with TestClient(app) as client:
            source_signup_response = client.post(
                "/accounts",
                json={
                    "tax_id": "52998224725",
                    "name": "John Doe",
                    "email": "john@example.com",
                },
            )
            destination_signup_response = client.post(
                "/accounts",
                json={
                    "tax_id": "11144477735",
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                },
            )
            source_account_id = source_signup_response.json()["account_id"]
            destination_account_id = destination_signup_response.json()["account_id"]
            source_wallet_id = self._get_wallet_id(app, source_account_id)
            destination_wallet_id = self._get_wallet_id(app, destination_account_id)

            client.post(
                f"/wallets/{source_wallet_id}/deposits",
                json={"amount": "100.00"},
                headers={"Idempotency-Key": "transfer-api-deposit-001"},
            )

            transfer_response = client.post(
                f"/wallets/{source_wallet_id}/transfers",
                json={
                    "destination_wallet_id": destination_wallet_id,
                    "amount": "25.00",
                },
                headers={"Idempotency-Key": "transfer-api-001"},
            )

        assert source_wallet_id is not None
        assert destination_wallet_id is not None
        assert transfer_response.status_code == 201
        assert transfer_response.json() == {
            "transaction_id": transfer_response.json()["transaction_id"],
            "source_wallet_id": source_wallet_id,
            "destination_wallet_id": destination_wallet_id,
            "amount": {
                "amount": "25.00",
                "currency": "BRL",
            },
            "transaction_type": "transfer",
            "status": "completed",
        }

    def test_transfer_returns_not_found_for_unknown_destination_wallet(self, tmp_path):
        database_url = f"sqlite:///{tmp_path / 'test.db'}"
        app = create_app(database_url=database_url)

        with TestClient(app) as client:
            signup_response = client.post(
                "/accounts",
                json={
                    "tax_id": "52998224725",
                    "name": "John Doe",
                    "email": "john@example.com",
                },
            )
            account_id = signup_response.json()["account_id"]
            wallet_id = self._get_wallet_id(app, account_id)

            client.post(
                f"/wallets/{wallet_id}/deposits",
                json={"amount": "100.00"},
                headers={"Idempotency-Key": "transfer-api-deposit-404"},
            )

            response = client.post(
                f"/wallets/{wallet_id}/transfers",
                json={
                    "destination_wallet_id": "123e4567-e89b-12d3-a456-426614174000",
                    "amount": "25.00",
                },
                headers={"Idempotency-Key": "transfer-api-404"},
            )

        assert wallet_id is not None
        assert response.status_code == 404
        assert response.json() == {"detail": "Wallet not found"}

    def test_transfer_returns_bad_request_for_same_wallet(self, tmp_path):
        database_url = f"sqlite:///{tmp_path / 'test.db'}"
        app = create_app(database_url=database_url)

        with TestClient(app) as client:
            signup_response = client.post(
                "/accounts",
                json={
                    "tax_id": "52998224725",
                    "name": "John Doe",
                    "email": "john@example.com",
                },
            )
            account_id = signup_response.json()["account_id"]
            wallet_id = self._get_wallet_id(app, account_id)

            response = client.post(
                f"/wallets/{wallet_id}/transfers",
                json={
                    "destination_wallet_id": wallet_id,
                    "amount": "25.00",
                },
                headers={"Idempotency-Key": "transfer-api-same-wallet"},
            )

        assert wallet_id is not None
        assert response.status_code == 400
        assert response.json() == {"detail": "Cannot transfer to the same wallet"}

    def test_transfer_requires_idempotency_key_header(self, tmp_path):
        database_url = f"sqlite:///{tmp_path / 'test.db'}"
        app = create_app(database_url=database_url)

        with TestClient(app) as client:
            source_signup_response = client.post(
                "/accounts",
                json={
                    "tax_id": "52998224725",
                    "name": "John Doe",
                    "email": "john@example.com",
                },
            )
            destination_signup_response = client.post(
                "/accounts",
                json={
                    "tax_id": "11144477735",
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                },
            )
            source_wallet_id = self._get_wallet_id(
                app,
                source_signup_response.json()["account_id"],
            )
            destination_wallet_id = self._get_wallet_id(
                app,
                destination_signup_response.json()["account_id"],
            )

            response = client.post(
                f"/wallets/{source_wallet_id}/transfers",
                json={
                    "destination_wallet_id": destination_wallet_id,
                    "amount": "25.00",
                },
            )

        assert source_wallet_id is not None
        assert destination_wallet_id is not None
        assert response.status_code == 422
