from django.contrib import admin
from profiles.models import Author, AuthorFriend, User

# Register Author and AuthorFriend model in admin.
admin.site.register(User)
admin.site.register(Author)
admin.site.register(AuthorFriend)
