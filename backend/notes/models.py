from django.db import models

# Create your models here.
from django.db import models

from django.db import models

class Note(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
