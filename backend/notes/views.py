from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from .models import Note, User
from .serializers import NoteSerializer, UserSerializer, TemporaryUserSerializer
import uuid
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .models import Note
from .serializers import NoteSerializer, UserSerializer
import uuid
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework import serializers



User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not all([username, email, password]):
            return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create token for immediate login
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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
        
        Note.objects.filter(local_id=local_id).update(user=user, local_id=None)
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
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
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            local_id = self.request.META.get('HTTP_X_LOCAL_ID')
            serializer.save(local_id=local_id)

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