from time import sleep

import requests


def test_hermes():
    payload = {"model": "hermes",
               "discussion_length": 2}
    response = requests.post("http://0.0.0.0:33333/discuss", json=payload)
    assert response.status_code == 200


def test_gpt():
    discussion_length = 2
    payload = {
        "model": "gpt",
        "prompt_names": ["advocate_discussant", "critic_discussant"],
        "question": "What is the best color sock?",
        "context": "teal is a good sock color",
        "discussion_length": discussion_length
    }
    response = requests.post("http://0.0.0.0:33333/discuss", json=payload)
    assert response.status_code == 200
    finished = False
    while not finished:
        sleep(1)
        response = requests.post("http://0.0.0.0:33333/poll")
        poll_payload = response.json()
        finished = poll_payload["finished"]
    dialog = poll_payload["dialog"]
    assert len(dialog) == discussion_length
    for message in dialog:
        print("\n\n<message>\n")
        print(message)
