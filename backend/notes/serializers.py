from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Note
# serializers.py
from rest_framework import serializers
from .models import Note, User

class TemporaryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'local_storage_id', 'username']
        extra_kwargs = {
            'username': {'required': False},
            'local_storage_id': {'read_only': True}
        }

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'local_id': {'required': False}
        }