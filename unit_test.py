import pytest
import json
import os
from app import create_app
from db import db

@pytest.fixture(scope="session")
def app():
    app = create_app(test=True)
    yield app

    os.unlink('test_twitter_clone.db')

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

def test_index(app, client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Hello, please register or login!' == json.loads(response.get_data(as_text=True))

def test_successful_registration(app, client):
    payload = {
        "username": "testuser",
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

def test_passwords_mismatch_registration(app, client):
    payload = {
        "username": "testuser2",
        "password": "testpassword1",
        "password2": "testpassword2"
    }
    response = client.post('/register', data=payload)
    assert response.status_code == 401
    assert {'error': 'Password mismatch!'} == json.loads(response.get_data(as_text=True))

def test_username_exists_registration(app, client):
    payload = {
        "username": "testuser",
        "password": "testpassword",
        "password2": "testpassword"
    }
    response = client.post('/register', data=payload)
    assert response.status_code == 409
    assert {'error': 'User exists, try another username!'} == json.loads(response.get_data(as_text=True))

def test_successful_login(app, client):
    payload = {
        "username": "testuser",
        "password": "testpassword"
    }
    response = client.post('/login', data=payload)
    assert response.status_code == 302
    assert "http://localhost/" == response.headers["Location"]

def test_missing_fields_login(app, client):
    payload = {
        "username": "",
        "password": ""
    }
    response = client.post('/login', data=payload)
    assert response.status_code == 400
    assert {'error': 'Fields are required to be filled.'} == json.loads(response.get_data(as_text=True))

def test_username_does_not_exist_login(app, client):
    payload = {
        "username": "testuser123",
        "password": "testpassword"
    }
    response = client.post('/login', data=payload)
    assert response.status_code == 404
    assert {'error':'Cannot find user with username ' + 'testuser123'} == json.loads(response.get_data(as_text=True))

def test_incorrect_password_login(app, client):
    payload = {
        "username": "testuser",
        "password": "testpassword123"
    }
    response = client.post('/login', data=payload)
    assert response.status_code == 401
    assert {'error': 'Incorrect password!'} == json.loads(response.get_data(as_text=True))
