import os
import django
from faker import Faker
import uuid
os.environ.setdefault('DJANGO_SETTINGS_MODULE','socialdistribution.settings')
django.setup()

fake = Faker()

from profiles.models import Author

def populateAuthor(n=50):
    for _ in range(n):
        fake_id = uuid.uuid4()
        fake_email = fake.email()
        fake_first_name = fake.first_name()
        fake_last_name = fake.last_name()
        fake_display_name = fake_first_name + " " + fake_last_name
        fake_bio = fake.text()
        #fake_host = "http://127.0.0.1:8000/"
        fake_github = "https://github.com/" + fake_first_name + fake_last_name

        Author.objects.get_or_create(id=fake_id, email=fake_email,
                                     firstName=fake_first_name,
                                     lastName=fake_last_name,
                                     displayName=fake_display_name,
                                     bio=fake_bio, # host=fake_host,
                                     github=fake_github)


if __name__ == "__main__":
    populateAuthor(300)
