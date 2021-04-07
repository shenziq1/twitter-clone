import pytest
import json
import os
from app import create_app
from db import db
from werkzeug.security import check_password_hash

# Create a test app
@pytest.fixture(scope='session')
def app():
    app = create_app(test=True)
    yield app

    # Delete test database after unit tests.
    os.unlink('test_twitter_clone.db')

# To make requests to the app.
@pytest.fixture(scope='session')
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
            'username': 'testuser',
            'password': 'testpassword',
            'password2': 'testpassword'
        }
        response = client.post('/register', data=payload)
        assert response.status_code == 302
        assert 'http://localhost/login' == response.headers['Location']

    def test_missing_fields_registration(app, client):
        payload = {
            'username': '',
            'password': '',
            'password2': ''
        }
        response = client.post('/register', data=payload)
        assert response.status_code == 400
        assert {'error': 'Fields are required to be filled.'} == json.loads(response.get_data(as_text=True))

    def test_passwords_mismatch_registration(app, client):
        payload = {
            'username': 'testuser2',
            'password': 'testpassword1',
            'password2': 'testpassword2'
        }
        response = client.post('/register', data=payload)
        assert response.status_code == 401
        assert {'error': 'Password mismatch!'} == json.loads(response.get_data(as_text=True))

    def test_username_exists_registration(app, client):
        payload = {
            'username': 'testuser',
            'password': 'testpassword',
            'password2': 'testpassword'
        }
        response = client.post('/register', data=payload)
        assert response.status_code == 409
        assert {'error': 'User exists, try another username!'} == json.loads(response.get_data(as_text=True))

    def test_users(app, client):
        response = client.get('/users')
        assert response.status_code == 200
        # Get password_hash in response, then check if it is the same as hashing input password again.
        assert check_password_hash(json.loads(response.get_data(as_text=True))[0]['password_hash'], 'testpassword') == True


################################################################################

class TestLogin:
    def test_successful_login(app, client):
        payload = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = client.post('/login', data=payload)
        assert response.status_code == 302
        assert 'http://localhost/' == response.headers['Location']

    def test_missing_fields_login(app, client):
        payload = {
            'username': '',
            'password': ''
        }
        response = client.post('/login', data=payload)
        assert response.status_code == 400
        assert {'error': 'Fields are required to be filled.'} == json.loads(response.get_data(as_text=True))

    def test_username_does_not_exist_login(app, client):
        payload = {
            'username': 'testuser123',
            'password': 'testpassword'
        }
        response = client.post('/login', data=payload)
        assert response.status_code == 404
        assert {'error':'Cannot find user with username ' + 'testuser123'} == json.loads(response.get_data(as_text=True))

    def test_incorrect_password_login(app, client):
        payload = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = client.post('/login', data=payload)
        assert response.status_code == 401
        assert {'error': 'Incorrect password!'} == json.loads(response.get_data(as_text=True))

    def test_logout(app, client):
        response = client.get('/logout')
        assert response.status_code == 302
        assert 'http://localhost/' == response.headers['Location']

################################################################################

class TestChat:
    def test_setup_chat(app, client):
        user_a = {
            'username': 'a',
            'password': '1',
            'password2': '1'
        }
        client.post('/register', data=user_a)

        user_b = {
            'username': 'b',
            'password': '2',
            'password2': '2'
        }
        client.post('/register', data=user_b)

    def test_chat_a(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        chat = {
            '_to': 'b',
            'content': 'hello, b'
        }
        response = client.post('/chat', data=chat)
        assert response.status_code == 200
        assert {'success': 'Message has been sent!'} == json.loads(response.get_data(as_text=True))

    def test_invalid_user_chat(app, client):
        payload = {
            '_to': 'c',
            'content': 'hello, c'
        }
        response = client.post('/chat', data=payload)
        assert response.status_code == 404
        assert {'error':'Cannot find user with username ' + 'c'} == json.loads(response.get_data(as_text=True))

    def test_missing_field_chat(app, client):
        payload = {
            '_to': '',
            'content': ''
        }
        response = client.post('/chat', data=payload)
        assert response.status_code == 400
        assert {'error': 'Fields are required to be filled.'} == json.loads(response.get_data(as_text=True))

        client.get('/logout')

################################################################################

class TestSentHistory:
    def test_sent_history_a(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        response = client.get('/history/sent')
        assert response.status_code == 200
        assert [{'_to': 'b', 'message': 'hello, b'}] == json.loads(response.get_data(as_text=True))

        client.get('/logout')

    def test_sent_empty_history_b(app, client):
        login = {
            'username': 'b',
            'password': '2'
        }
        client.post('/login', data=login)

        response = client.get('/history/sent')
        assert response.status_code == 200
        assert [] == json.loads(response.get_data(as_text=True))

        client.get('/logout')

################################################################################

class TestReceivedHistory:
    def test_received_empty_history_a(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        response = client.get('/history/received')
        assert response.status_code == 200
        assert [] == json.loads(response.get_data(as_text=True))

        client.get('/logout')

    def test_received_history_b(app, client):
        login = {
            'username': 'b',
            'password': '2'
        }
        client.post('/login', data=login)

        response = client.get('/history/received')
        assert response.status_code == 200
        assert [{'_from': 'a', 'message': 'hello, b'}] == json.loads(response.get_data(as_text=True))

        client.get('/logout')

################################################################################

class TestTweet:
    def test_successful_tweet(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        tweet = {
            'title': 'this is title',
            'content': 'this is content'
        }
        response = client.post('/tweet', data=tweet)
        assert response.status_code == 200
        assert {'success': 'Tweet has been posted!'} == json.loads(response.get_data(as_text=True))

        client.get('/logout')

    def test_empty_tweet(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        tweet = {
            'title': '',
            'content': ''
        }
        response = client.post('/tweet', data=tweet)
        assert response.status_code == 400
        assert {'error': 'Fields are required to be filled.'} == json.loads(response.get_data(as_text=True))

        client.get('/logout')

    def test_view_tweet(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        response = client.get('/tweet')
        assert response.status_code == 200
        assert [{
            'author': 'a',
            'content': 'this is content',
            'like': 0,
            'title': 'this is title',
            'tweet_id': 1
        }] == json.loads(response.get_data(as_text=True))

        client.get('/logout')

    def test_update_tweet(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        new_tweet = {
            'tweet_id':'1',
            'title':'title',
            'content':'content'
        }

        response = client.put('/tweet', data=new_tweet)
        assert response.status_code == 200
        assert {'success': 'Tweet has been updated!'} == json.loads(response.get_data(as_text=True))

        response2 = client.get('/tweet')
        assert response.status_code == 200
        assert [{
            'author': 'a',
            'content': 'content',
            'like': 0,
            'title': 'title',
            'tweet_id': 1
        }] == json.loads(response2.get_data(as_text=True))

        client.get('/logout')

    def test_update_not_found_tweet(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        new_tweet = {
            'tweet_id':'2',
            'title':'title',
            'content':'content'
        }

        response = client.put('/tweet', data=new_tweet)
        assert response.status_code == 404
        assert {'error': 'Tweet Not Found.'} == json.loads(response.get_data(as_text=True))

        client.get('/logout')

    def test_update_empty_tweet(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        new_tweet = {
            'tweet_id':'',
            'title':'',
            'content':''
        }

        response = client.put('/tweet', data=new_tweet)
        assert response.status_code == 400
        assert {'error': 'Fields are required to be filled.'} == json.loads(response.get_data(as_text=True))

        client.get('/logout')

    def test_delete_tweet(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        response = client.delete('/tweet', data={'tweet_id': '1'})
        assert response.status_code == 200
        assert {'success': 'Tweet has been deleted!'} == json.loads(response.get_data(as_text=True))

        client.get('/logout')

    def test_delete_empty_tweet(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        response = client.delete('/tweet', data={'tweet_id': ''})
        assert response.status_code == 400
        assert {'error': 'Fields are required to be filled.'} == json.loads(response.get_data(as_text=True))

        client.get('/logout')

    def test_delete_not_found_tweet(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        response = client.delete('/tweet', data={'tweet_id': '1'})
        assert response.status_code == 404
        assert {'error': 'Tweet Not Found'} == json.loads(response.get_data(as_text=True))

        client.get('/logout')

################################################################################

class TestLike():
    def test_successful_like(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        tweet = {
            'title': 'this is title',
            'content': 'this is content'
        }
        client.post('/tweet', data=tweet)

        response = client.post('/like', data={'tweet_id': '1'})
        assert response.status_code == 200
        assert {'success': 'Liked the Tweet! Like count is now 1!'} == json.loads(response.get_data(as_text=True))

        response2 = client.get('/tweet')
        assert response.status_code == 200
        assert [{
            'author': 'a',
            'content': 'this is content',
            'like': 1,
            'title': 'this is title',
            'tweet_id': 1
        }] == json.loads(response2.get_data(as_text=True))

        client.get('logout')

################################################################################

class TestUnlike():
    def test_successful_like(app, client):
        login = {
            'username': 'a',
            'password': '1'
        }
        client.post('/login', data=login)

        response = client.post('/unlike', data={'tweet_id': '1'})
        assert response.status_code == 200
        assert {'success': 'Unliked the Tweet! Like count is now 0!'} == json.loads(response.get_data(as_text=True))

        response2 = client.get('/tweet')
        assert response.status_code == 200
        assert [{
            'author': 'a',
            'content': 'this is content',
            'like': 0,
            'title': 'this is title',
            'tweet_id': 1
        }] == json.loads(response2.get_data(as_text=True))

        client.get('logout')
