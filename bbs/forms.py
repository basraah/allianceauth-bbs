from django import forms
from django.db import transaction
from martor.fields import MartorFormField
from . import models

import logging

logger = logging.getLogger(__name__)


class PostForm(forms.ModelForm):
    content = MartorFormField()

    class Meta:
        model = models.Post
        fields = ('content',)


class TopicForm(forms.ModelForm):
    content = MartorFormField()

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['category'].queryset = models.Category.objects.all().visible_for_user(user)

    @transaction.atomic
    def save(self, commit=True):
        instance = super().save()
        post = models.Post()
        post.content = self.cleaned_data.get('content')
        post.created_by = self.user
        post.topic = instance
        post.save()
        return instance

    class Meta:
        model = models.Topic
        fields = ('title', 'category', 'content')
