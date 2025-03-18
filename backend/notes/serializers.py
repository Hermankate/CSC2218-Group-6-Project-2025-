from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Note

User = get_user_model()
# serializers.py
from rest_framework import serializers
from .models import Note, User
from django.contrib.auth.password_validation import validate_password

class TemporaryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'local_storage_id']
        extra_kwargs = {'username': {'required': False}}

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'
        extra_kwargs = {'user': {'required': False}}