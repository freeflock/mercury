import requests


def test_discuss():
    payload = {"model": "hermes", "system_prompt": "hermes trismegistus"}
    response = requests.post("http://0.0.0.0:33333/discuss", json=payload)
    assert response.status_code == 200
