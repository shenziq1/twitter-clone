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

################################################################################
class TestBase:
    def test_index(app, client):
        response = client.get('/')
        assert response.status_code == 200
        assert 'Hello, please register or login!' == json.loads(response.get_data(as_text=True))

################################################################################
class TestRegistration:
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

################################################################################

class TestLogin:
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

    def test_logout(app, client):
        response = client.get('/logout')
        assert response.status_code == 302
        assert "http://localhost/" == response.headers["Location"]

################################################################################

class TestChat:
    def test_setup_chat(app, client):
        payload1 = {
            "username": "a",
            "password": "1",
            "password2": "1"
        }
        client.post('/register', data=payload1)

        payload2 = {
            "username": "b",
            "password": "2",
            "password2": "2"
        }
        client.post('/register', data=payload2)

        payload3 = {
            "username": "b",
            "password": "2"
        }
        client.post('/login', data=payload3)

    def test_chat(app, client):
        payload = {
            "_to": "a",
            "content": "hello, a"
        }
        response = client.post('/chat', data=payload)
        assert response.status_code == 200

    def test_invalid_user_chat(app, client):
        payload = {
            "_to": "c",
            "content": "hello, c"
        }
        response = client.post('/chat', data=payload)
        assert response.status_code == 404

    def test_missing_field_chat(app, client):
        payload = {
            "_to": "",
            "content": ""
        }
        response = client.post('/chat', data=payload)
        assert response.status_code == 400
