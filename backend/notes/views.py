
from django.db import IntegrityError
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from .models import Note
from .serializers import NoteSerializer, UserSerializer, TemporaryUserSerializer
import uuid
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers

User = get_user_model()
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        username = request.data.get('username', '')  # Optional
        email = request.data.get('email')
        password = request.data.get('password')

        if not all([email, password]):
            return Response({'error': 'Email and password are required'}, status=400)

        user = User.objects.create_user(
            email=email,
            password=password,
            username=username  # Optional field
        )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        }, status=201)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
@api_view(['POST'])
@permission_classes([AllowAny])
def sync_notes(request):
    try:
        local_id = request.data.get('local_storage_id')
        notes = request.data.get('notes', [])
        
        user, created = User.objects.get_or_create(
            local_storage_id=local_id,
            defaults={
                'username': f"temp_{uuid.uuid4().hex[:8]}",
                'is_temporary': True
            }
        )
        
        for note_data in notes:
            Note.objects.update_or_create(
                local_id=note_data.get('local_id'),
                defaults={
                    'title': note_data['title'],
                    'content': note_data['content'],
                    'category': note_data.get('category', 'Uncategorized'),
                    'user': user
                }
            )
        
        Note.objects.filter(local_id=local_id).update(user=user, local_id=None)
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class NoteListCreateView(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Note.objects.filter(user=self.request.user)
        local_id = self.request.META.get('HTTP_X_LOCAL_ID')
        return Note.objects.filter(local_id=local_id)

    def perform_create(self, serializer):
        note_data = {
            **serializer.validated_data,
            'category': self.request.data.get('category', 'Uncategorized')
        }
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user, **note_data)
        else:
            local_id = self.request.META.get('HTTP_X_LOCAL_ID')
            serializer.save(local_id=local_id, **note_data)

class NoteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Note.objects.filter(user=self.request.user)
        local_id = self.request.META.get('HTTP_X_LOCAL_ID')
        return Note.objects.filter(local_id=local_id)

class EmailAuthTokenSerializer(AuthTokenSerializer):
    username = serializers.CharField(
        label="Email",
        write_only=True
    )

class CustomAuthToken(ObtainAuthToken):
    serializer_class = EmailAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            }
        })