from app.main import healthcheck


def test_healthcheck():
    assert healthcheck() == "ok"
