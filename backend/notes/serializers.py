# serializers.py
from rest_framework import serializers
from .models import Note, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username']

class NoteSerializer(serializers.ModelSerializer):
    tagged_users = UserSerializer(many=True, read_only=True)
    tagged_emails = serializers.ListField(
        child=serializers.EmailField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Note
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True},
            'local_id': {'read_only': True}
        }

    def create(self, validated_data):
        tagged_emails = validated_data.pop('tagged_emails', [])
        note = super().create(validated_data)
        self._process_tagged_users(note, tagged_emails)
        return note

    def update(self, instance, validated_data):
        tagged_emails = validated_data.pop('tagged_emails', [])
        note = super().update(instance, validated_data)
        note.tagged_users.clear()
        self._process_tagged_users(note, tagged_emails)
        return note

    def _process_tagged_users(self, note, emails):
        users = User.objects.filter(email__in=emails)
        note.tagged_users.add(*users)