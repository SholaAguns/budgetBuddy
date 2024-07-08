from django.contrib import auth
from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class User(auth.models.User, auth.models.PermissionsMixin):
    slug = models.SlugField(allow_unicode=True, unique=True, max_length=200)
    created_dt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "@{}".format(self.username)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.created_dt = timezone.now()
        super().save(*args, **kwargs)
