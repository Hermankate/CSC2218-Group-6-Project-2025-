from rest_framework import serializers
from .models import Note, User
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'email': {'required': False}
        }

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