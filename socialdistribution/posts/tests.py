from django.test import TestCase, Client
from django.shortcuts import render
from django.contrib.auth import get_user_model
from .models import Post, Comment
from datetime import *
import uuid

# Create your tests here.
class Profiles_Test(TestCase):
    def setUp(self):
        print("HER")

    def test_this_does_something(self):
        print("HERRO")
        User = get_user_model()
        user = User.objects.create_superuser('to@to.com', 'wrongaccount')
        x = Post.objects.create(title = "derp", published = datetime.now(), author = user)
        print("WORKED")
