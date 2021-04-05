import pytest
import json
from app import app as flask_app
from db import db

@pytest.fixture
def app():
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index(app, client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Hello, please register or login!' == json.loads(response.get_data(as_text=True))

def test_successful_registration(app, client):
    payload = {
        "username": "testuser7",
        "password": "testpassword",
        "password2": "testpassword"
    }
    response = client.post('/register', data=payload)
    assert response.status_code == 302
    assert "http://localhost/login" == response.headers["Location"]

def test_missing_fields_registration(app, client):
    payload = {
        "username": "",
        "password": "",
        "password2": ""
    }
    response = client.post('/register', data=payload)
    assert response.status_code == 400
    assert {'error': 'Fields are required to be filled.'} == json.loads(response.get_data(as_text=True))

def test_username_exists_registration(app, client):
    payload = {
        "username": "testuser7",
        "password": "testpassword7",
        "password2": "testpassword7"
    }
    response = client.post('/register', data=payload)
    assert response.status_code == 409
    assert {'error': 'User exists, try another username!'} == json.loads(response.get_data(as_text=True))
