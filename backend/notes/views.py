from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .models import Note
from .serializers import NoteSerializer, UserSerializer
# views.py
from rest_framework.decorators import api_view

@api_view(['POST'])
def sync_notes(request):
    # Handle local storage sync logic
    pass

class NoteListCreateView(generics.ListCreateAPIView):
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Note.objects.filter(user=self.request.user)
        return Note.objects.filter(local_id=self.request.data.get('local_storage_id'))

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save(local_id=self.request.data.get('local_storage_id'))