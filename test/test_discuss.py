import os
from time import sleep

import requests

API_KEY = os.getenv("API_KEY")


def test_no_api_key():
    response = requests.post("http://0.0.0.0:33333/discuss", json={})
    assert response.status_code == 403


def test_wrong_api_key():
    headers = {"x-api-key": "nonsense"}
    response = requests.post("http://0.0.0.0:33333/discuss", headers=headers, json={})
    assert response.status_code == 403


def test_hermes():
    headers = {"x-api-key": API_KEY}
    payload = {"model": "hermes",
               "discussion_length": 2}
    response = requests.post("http://0.0.0.0:33333/discuss", headers=headers, json=payload)
    assert response.status_code == 200


def test_gpt():
    discussion_length = 2
    headers = {"x-api-key": API_KEY}
    payload = {
        "model": "gpt",
        "prompt_names": ["advocate_discussant", "critic_discussant"],
        "question": "What is the best color sock?",
        "context": "teal is a good sock color",
        "discussion_length": discussion_length
    }
    response = requests.post("http://0.0.0.0:33333/discuss", headers=headers, json=payload)
    assert response.status_code == 200
    finished = False
    while not finished:
        sleep(1)
        response = requests.post("http://0.0.0.0:33333/poll", headers=headers)
        poll_payload = response.json()
        finished = poll_payload["finished"]
    dialog = poll_payload["dialog"]
    assert len(dialog) == discussion_length
    for message in dialog:
        print("\n\n<message>\n")
        print(message)
