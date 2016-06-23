import pytest
from sots import app


@pytest.fixture
def client(request):
    client = app.test_client()

    def teardown():
        pass
    request.addfinalizer(teardown)

    return client

def test_home(client):
    rv = client.get('/')
    assert rv.status_code == 400


