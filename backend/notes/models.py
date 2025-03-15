from django.db import models

# Create your models here.
from django.db import models

from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):  # Extending the default Django User model
    email = models.EmailField(unique=True)

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow null users
    title = models.CharField(max_length=200)
    content = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
