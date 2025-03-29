# models.py
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    is_temporary = models.BooleanField(default=False)
    local_storage_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=False,
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Note(models.Model):
    CATEGORY_CHOICES = [
        ('Uncategorized', 'Uncategorized'),
        ('Business', 'Business'),
        ('Family', 'Family'),
        ('Friends', 'Friends'),
        ('Personal', 'Personal'),
        ('Tagged', 'Tagged'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes',
        blank=True,
        null=True
    )
    local_id = models.UUIDField(default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Uncategorized')
    tagged_users = models.ManyToManyField(
        User,
        related_name='tagged_notes',
        blank=True
    )
    is_synced = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'local_id']),
            models.Index(fields=['local_id'])
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.title} - {self.user.email if self.user else 'Anonymous'}"

class Share(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    accessed_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Share of {self.note.title}"