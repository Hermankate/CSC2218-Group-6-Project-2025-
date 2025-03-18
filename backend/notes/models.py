import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True, null=True, blank=True)
    is_temporary = models.BooleanField(default=False)
    local_storage_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    local_id = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_synced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        indexes = [
            models.Index(fields=['user', 'local_id']),
            models.Index(fields=['local_id'])
        ]