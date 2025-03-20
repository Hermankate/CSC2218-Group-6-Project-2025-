from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from .models import Note, User
from .serializers import NoteSerializer, UserSerializer, TemporaryUserSerializer
import uuid
# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        try:
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
@api_view(['POST'])
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