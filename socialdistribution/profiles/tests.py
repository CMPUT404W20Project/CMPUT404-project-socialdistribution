from django.test import TestCase, Client
from django.shortcuts import render
from django.contrib.auth import get_user_model

# Create your tests here.
class Profiles_Test(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_superuser('to@to.com', 'wrongaccount')


    def test_account_login_1(self):
        User = get_user_model()
        client = Client()

        # Logging in, and retreiving stream (can only do when logged in)
        login_action = client.login( email='to@to.com', password='wrongaccount')
        login_stream = client.get('/accounts/password_change/')
        self.assertTrue(login_stream.status_code == 200)

        # Logout, and retreive stream (returns HTTP 302 to redirect to /accounts/login)
        logout_action = client.get('/accounts/logout/')
        logout_stream = client.get('/accounts/password_change/')
        self.assertTrue(logout_stream.status_code == 302)
        self.assertTrue("/accounts/login" in logout_stream.url)

