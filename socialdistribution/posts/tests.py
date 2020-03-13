from django.test import TestCase, Client
from django.shortcuts import render
from django.contrib.auth import get_user_model
from .models import Post, Comment
# from ..profiles.models import Author
from datetime import *
from django.utils import timezone
import uuid
from django.core.exceptions import ValidationError
import json

# Create your tests here.
class Profiles_Test(TestCase):
    
    # Post requires an author model
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser('to@to.com', 'wrongaccount')

    # Required fields for posts are :
    #   - Author object, date, title
    def test_create_post_object(self):
        User = get_user_model()

        try:
            Post.objects.create(title = "derp", published = timezone.now(), author = self.user)
        except:
            self.assertFalse(True)
    
    def test_invalid_user_object(self): # Models requires actual author instance, not uuid.
        try:
            Post.objects.create(title = "derp", published = timezone.now(), author = self.user.id)
        except ValueError: # ValueError means that the author variable is incorrect.
            self.assertTrue(True)
        except: #All other errors are incorrect.
            self.assertTrue(False)

    # Make sure that post made is put in table.
    def test_post_retrieval(self):
        self.post_made = Post.objects.create(title = "derp", published = timezone.now(), author = self.user)
        post_from_table = Post.objects.get(id = self.post_made.id)
   
        self.assertTrue(post_from_table == self.post_made)

    # Test that the model rejects a long title
    def test_post_title_too_long(self):
        long_title = ""
        for i in range(202):
            long_title += "e"
        
        try:
            self.post_made = Post.objects.create(title = long_title, published = timezone.now(), author = self.user, visibileTo = "Public")
            self.post_made.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except ValidationError as e:
            dict_of_error = json.loads(str(e).replace("'",'''"'''))
            error_message = 'Ensure this value has at most 200 characters'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['title']))
        except:
            self.assertFalse(True)


        # title, descriptions, categories, content_type, visibility
    

