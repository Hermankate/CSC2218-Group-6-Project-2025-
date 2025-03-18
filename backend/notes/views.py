from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .models import Note, User
from .serializers import NoteSerializer
# views.py
import uuid
from rest_framework.decorators import api_view
# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import Note, User
from .serializers import NoteSerializer, UserSerializer, TemporaryUserSerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data.get('email'),
            password=serializer.validated_data['password']
        )
        
        token = Token.objects.create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

# Keep the existing sync_notes and NoteListCreateView code below

@api_view(['POST'])
def sync_notes(request):
    try:
        # Handle local storage sync
        local_id = request.data.get('local_storage_id')
        notes = request.data.get('notes', [])
        
        # Get or create temporary user
        user, created = User.objects.get_or_create(
            local_storage_id=local_id,
            defaults={
                'username': f"temp_{uuid.uuid4().hex[:8]}",
                'is_temporary': True
            }
        )
        
        # Update notes with user relationship
        Note.objects.filter(local_id=local_id).update(user=user, local_id=None)
        
        # Return sync token
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class NoteListCreateView(generics.ListCreateAPIView):
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Note.objects.filter(user=self.request.user)
        local_id = self.request.META.get('HTTP_X_LOCAL_ID')
        return Note.objects.filter(local_id=local_id)

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            local_id = self.request.META.get('HTTP_X_LOCAL_ID')
            serializer.save(local_id=local_id)