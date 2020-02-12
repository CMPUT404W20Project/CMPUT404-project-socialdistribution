from django import forms

from .models import (Comment,
                     Post)


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = [
            'title',
            'description',
            'author',
            'categories',
            'visibility',
            'visibileTo',
        ]


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = [
            'author',
            'comment',
            'published',
        ]
