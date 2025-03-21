# # import uuid
# # from django.db import models
# # from django.contrib.auth.models import AbstractUser

# # class User(AbstractUser):
# #     email = models.EmailField(unique=True, null=True, blank=True)
# #     is_temporary = models.BooleanField(default=False)
# #     local_storage_id = models.CharField(max_length=100, null=True, blank=True)
# #     created_at = models.DateTimeField(auto_now_add=True)

# # class Note(models.Model):
# #     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
# #     local_id = models.CharField(max_length=100, null=True, blank=True)
# #     title = models.CharField(max_length=200)
# #     content = models.TextField()
# #     is_synced = models.BooleanField(default=False)
# #     created_at = models.DateTimeField(auto_now_add=True)
# #     updated_at = models.DateTimeField(auto_now=True)
    

# #     class Meta:
# #         indexes = [
# #             models.Index(fields=['user', 'local_id']),
# #             models.Index(fields=['local_id'])
# #         ]

# import uuid
# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.utils.translation import gettext_lazy as _

# class User(AbstractUser):
#     email = models.EmailField(_('email address'), unique=True)
#     is_temporary = models.BooleanField(default=False)
#     local_storage_id = models.CharField(max_length=100, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     # Add these to remove username field warnings
#     username = models.CharField(
#         _('username'),
#         max_length=150,
#         unique=False,  # Changed to allow multiple users without username
#         blank=True,
#         null=True
#     )

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = []  # Remove 'username' from required fields

#     def __str__(self):
#         return self.email

# class Note(models.Model):
#     user = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name='notes',
#         blank=True,
#         null=True
#     )
#     local_id = models.UUIDField(default=uuid.uuid4, editable=False)  # Better for UUIDs
#     title = models.CharField(max_length=200)
#     content = models.TextField()
#     is_synced = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         indexes = [
#             models.Index(fields=['user', 'local_id']),
#             models.Index(fields=['local_id'])
#         ]
#         ordering = ['-updated_at']

#     def __str__(self):
#         return f"{self.title} - {self.user.email if self.user else 'Anonymous'}"
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

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

    def __str__(self):
        return self.email

class Note(models.Model):
    CATEGORY_CHOICES = [
        ('Uncategorized', 'Uncategorized'),
        ('Business', 'Business'),
        ('Family', 'Family'),
        ('Friends', 'Friends'),
        ('Personal', 'Personal'),
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