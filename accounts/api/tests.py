from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User


LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


class AccountApiTests(TestCase):

    def setUp(self):
        # this function will be triggerred while test function is executed
        self.client = APIClient()
        self.user = self.createUser(
            username='admin',
            email='admin@jiuzhang.com',
            password='correct password',
        )

    def createUser(self, username, email, password):
        # cannot be User.objects.create()
        # password is encrypted, so username and email need to be normalized
        return User.objects.create_user(username, email, password)

    def test_login(self):
        # test functions names need to start with 'test', in order to be triggered by tests
        # test must be post, not get
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # login failed，http status code returns 405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code, 405)

        # uses 'post' but wrong password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # test not yet login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)
        # with correct password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@jiuzhang.com')
        # test already login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # login
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # test the user has logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # test must use 'post'
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # change to post should logout successfully
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)
        # test user has logged out
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        }
        # test get request fails
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # test wrong email
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # test password is too short
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': '123',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # test username is too long
        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # successful sign up
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')
        # test user has logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)