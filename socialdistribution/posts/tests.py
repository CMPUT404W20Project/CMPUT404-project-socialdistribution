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
        self.example_post = Post.objects.create(title = "short", published = timezone.now(), author = self.user, visibileTo = "Public")

    
    def fix_error_formating(self, x):
        x = x.replace("'", '"', 2)
        return(x)

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

    # Test that the model rejects a long description
    def test_descriptions_title_too_long(self):
        long_description = ""
        for i in range(202):
            long_description += "e"
        
        try:
            self.post_made = Post.objects.create(title = "short", published = timezone.now(), author = self.user, visibileTo = "Public", \
            description = long_description)
            self.post_made.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except ValidationError as e:
            dict_of_error = json.loads(str(e).replace("'",'''"'''))
            error_message = 'Ensure this value has at most 200 characters'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['description']))
        except:
            self.assertFalse(True)

    # Test that the model rejects an invalid categories setting
    def test_invalid_categories(self):      
        try:
            self.post_made = Post.objects.create(title = "short", published = timezone.now(), author = self.user, visibileTo = "Public", \
            categories = "invalid")
            self.post_made.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except ValidationError as e:

            error_string = self.fix_error_formating(str(e))
            dict_of_error = json.loads(error_string)
            error_message = 'is not a valid choice'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['categories']))
        except:
            self.assertFalse(True)

    # Test that the model rejects an invalid content setting
    def test_invalid_content(self):      
        try:
            self.post_made = Post.objects.create(title = "short", published = timezone.now(), author = self.user, visibileTo = "Public", \
            content_type = "invalid")
            self.post_made.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except ValidationError as e:

            error_string = self.fix_error_formating(str(e))
            dict_of_error = json.loads(error_string)
            error_message = 'is not a valid choice'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['content_type']))
        except:
            self.assertFalse(True)

    # Test that the model rejects an invalid content setting
    def test_content_visibility(self):      
        try:
            self.post_made = Post.objects.create(title = "short", published = timezone.now(), author = self.user, visibileTo = "Public", \
            visibility = "invalid")
            self.post_made.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except ValidationError as e:

            error_string = self.fix_error_formating(str(e))
            dict_of_error = json.loads(error_string)
            error_message = 'is not a valid choice'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['visibility']))
        except:
            self.assertFalse(True)            

    def test_post_invalid_user(self):
        modified_user = self.user
        modified_user.id = uuid.uuid1()
        post_made = Post.objects.create(title = "short", published = timezone.now(), author = modified_user, visibileTo = "Public")        
        try:
            post_made.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except Exception as e:
            error_string = self.fix_error_formating(str(e))
            dict_of_error = json.loads(error_string)
            error_message = 'does not exist'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['author']))   

    def test_post_delete_user(self):
        print("Implement me")  

    def test_post_non_user(self):
        print("Implement me") 

    # Try to create comment
    def test_comment_creation(self):
        try:
            comment_made = Comment.objects.create(author = self.user, post = self.example_post, comment = "hi")
            comment_made.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
            self.assertTrue(True)
        except:
            self.assertFalse(True)

    # Make sure that post made is put in table.
    def test_comment_retrieval(self):
        comment_made = Comment.objects.create(author = self.user, post = self.example_post, comment = "hi")
        comment_from_table = Comment.objects.get(id = comment_made.id)
   
        # Check that retrieved comment is the same as that submitted.
        self.assertTrue(comment_from_table == comment_made)

    def test_comment_invalid_type(self):
        try:
            comment_made = Comment.objects.create(author = self.user, post = self.example_post, comment = "hi", \
            content_type = "invalid")
            comment_made.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except ValidationError as e:
            error_string = self.fix_error_formating(str(e))
            dict_of_error = json.loads(error_string)
            error_message = 'is not a valid choice'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['content_type']))
        except:
            self.assertFalse(True)

    def test_invalid_user(self):
        modified_user = self.user
        modified_user.id = uuid.uuid1()
        comment_made = Comment.objects.create(author = modified_user, post = self.example_post, comment = "hi")
        comment_from_table = Comment.objects.get(id = comment_made.id)
        try:
            comment_made.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except Exception as e:
            error_string = self.fix_error_formating(str(e))
            dict_of_error = json.loads(error_string)
            error_message = 'does not exist'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['author']))

    def test_invalid_post(self):
        modified_post = self.example_post
        modified_post.id = uuid.uuid1()
        comment_made = Comment.objects.create(author = self.user, post = modified_post, comment = "hi")
        
        try:
            comment_made.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except Exception as e:
            error_string = self.fix_error_formating(str(e))
            dict_of_error = json.loads(error_string)
            error_message = 'does not exist'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['post']))        

    def test_comment_delete_user(self):
        print("Implement me")

    def test_comment_delete_post(self):
        print("Implement me")