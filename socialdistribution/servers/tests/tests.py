import uuid
from django.test import TestCase
from servers.models import Server
from faker import Faker
from profiles.utils import getAuthorFriendRelationships, getFriendsOfAuthor,\
                    getFriendRequestsToAuthor, getFriendRequestsFromAuthor,\
                    isFriend
from django.test import Client
from django.contrib.auth import get_user_model
import uuid
from django.core.exceptions import ValidationError
import sys
import json

faker = Faker()

class ServersTest(TestCase):

    def create_valid_server(self):
        url = faker.url()
        api_location = faker.url()

        remote_server_user = faker.first_name()
        remote_server_pass = faker.password()

        local_server_user = uuid.uuid4()
        local_server_pass = faker.password()
        
        # permissions for server
        is_active = True
        share_posts = True
        share_images = True

        return Server.objects.create(url = url, api_location = api_location, remote_server_pass = remote_server_pass,
                                    remote_server_user = remote_server_user, local_server_pass = local_server_pass,
                                    local_server_user = local_server_user, is_active = is_active, 
                                    share_posts = share_posts, share_images = share_images)

    def create_too_long_field(self):
        x = "i"  * 256
        return(x)

    def test_url_too_long(self):
        self.create_too_long_field()
        server_object = self.create_valid_server()
        server_object.url = "iii"
        try:
            server_object.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except ValidationError as e:
            dict_of_error = json.loads(str(e).replace("'",'''"'''))
            error_message = 'Enter a valid URL'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['url']))
        except:
            self.assertFalse(True)
    
    def test_api_location_too_long(self):
        self.create_too_long_field()
        server_object = self.create_valid_server()
        server_object.api_location = self.create_too_long_field()
        try:
            server_object.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except ValidationError as e:
            dict_of_error = json.loads(str(e).replace("'",'''"'''))
            error_message = 'Enter a valid URL'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['api_location']))
        except:
            self.assertFalse(True)
        
    def test_url_field_not_url(self):
        self.create_too_long_field()
        server_object = self.create_valid_server()
        server_object.url = "1.com/" + self.create_too_long_field()
        try:
            server_object.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except ValidationError as e:
            dict_of_error = json.loads(str(e).replace("'",'''"'''))
            error_message = 'Enter a valid URL'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['url']))
        except:
            self.assertFalse(True)
    
    def test_api_location_no_url(self):
        self.create_too_long_field()
        server_object = self.create_valid_server()
        server_object.api_location = "1.com/" + self.create_too_long_field()
        try:
            server_object.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except ValidationError as e:
            dict_of_error = json.loads(str(e).replace("'",'''"'''))
            error_message = 'Enter a valid URL'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['api_location']))
        except:
            self.assertFalse(True)

    def test_local_server_user_not_uuid(self):
        self.create_too_long_field()
        server_object = self.create_valid_server()
        server_object.local_server_user = "i"
        try:
            server_object.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except ValidationError as e:
            dict_of_error = json.loads(str(e).replace("'",'''"'''))
            error_message = 'is not a valid UUID'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['local_server_user']))
        except:
            self.assertFalse(True)

    def test_remote_server_user_too_long(self):
        self.create_too_long_field()
        server_object = self.create_valid_server()
        server_object.remote_server_user = self.create_too_long_field()
        try:
            server_object.full_clean() # NOTE: Have to run .full_clean() on object to check fields.
        except ValidationError as e:
            dict_of_error = json.loads(str(e).replace("'",'''"'''))
            error_message = 'Ensure this value has at most 255 characters'
            self.assertTrue(len(dict_of_error) == 1)
            self.assertTrue(error_message in str(dict_of_error['remote_server_user']))
        except:
            self.assertFalse(True)

    def test_server_actions_with_permissions(self):
        pass

