import falcon
from falcon import testing
import pytest

from promenade.control.api import ValidateDesignResource
from promenade.promenade import promenade


@pytest.fixture()
def client():
    return testing.TestClient(promenade)

def test_post_validatedesign_fail(client):
    response = client.simulate_post('/api/v1.0/validatedesign')
    assert response.status == falcon.HTTP_400
    body = response.content.decode('utf-8')
    assert '"reason": "Missing Parameter"' in body
    assert '"status": "Failure"' in body

def test_post_validatedesign(client):
    response = client.simulate_post('/api/v1.0/validatedesign?href=deckhand+http://deckhand.ucp.svc.cluster.local')
    assert response.status == falcon.HTTP_200
    body = response.content.decode('utf-8')
    assert '"kind": "Status"' in body
    assert '"reason": "Validation"' in body
    assert '"status": "Valid"' in body
