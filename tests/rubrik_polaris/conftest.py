import io
import json
import pytest
from rubrik_polaris.rubrik_polaris import PolarisClient

BASE_URL = "https://rubrik-se-beta.my.rubrik.com/api"


def util_load_json(path: str) -> dict:
    """Load a json to python dict."""
    with io.open(path, mode='r', encoding='utf-8') as f:
        return json.loads(f.read())


@pytest.fixture()
def client(requests_mock):
    data = {
        "access_token": "dummy",
        "mfa_token": "dummy_token"
    }
    requests_mock.post(BASE_URL + "/session", json=data)
    client_obj = PolarisClient(
        domain="rubrik-se-beta",
        username="dummy_username",
        password="dummy_password",
        insecure=True
    )
    return client_obj
