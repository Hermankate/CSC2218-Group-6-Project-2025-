from django.db import models

# Create your models here.
from django.db import models

from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models
# models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True, blank=True, null=True)
    is_temporary = models.BooleanField(default=False)
    local_storage_id = models.CharField(max_length=100, blank=True, null=True)

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    local_id = models.CharField(max_length=100, blank=True, null=True)
    is_synced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)