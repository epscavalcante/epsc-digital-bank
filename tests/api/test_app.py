from fastapi.testclient import TestClient

from app.main import create_app


class TestApi:
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

            deposit_response = client.post(
                f"/accounts/{account_id}/deposits",
                json={
                    "amount": "100.00",
                    "idempotency_key": "deposit-api-001",
                },
            )

        assert deposit_response.status_code == 201
        assert deposit_response.json() == {
            "transaction_id": deposit_response.json()["transaction_id"],
            "account_id": account_id,
            "amount": {
                "amount": "100.00",
                "currency": "BRL",
            },
            "transaction_type": "deposit",
            "status": "completed",
        }

    def test_deposit_returns_not_found_for_unknown_account(self, tmp_path):
        database_url = f"sqlite:///{tmp_path / 'test.db'}"
        app = create_app(database_url=database_url)

        with TestClient(app) as client:
            response = client.post(
                "/accounts/123e4567-e89b-12d3-a456-426614174000/deposits",
                json={
                    "amount": "100.00",
                },
            )

        assert response.status_code == 404
        assert response.json() == {"detail": "Account not found"}
