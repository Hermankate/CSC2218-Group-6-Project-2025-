
from django.db import IntegrityError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from notique import settings
from .models import Note, Share
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
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response


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

# # In your Django views.py
# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def share_note(request, note_id):
#     note = get_object_or_404(Note, id=note_id, user=request.user)
#     return Response({
#         "share_url": f"{settings.BASE_URL}/shared/{note_id}/",
#         "title": note.title,
#         "content": note.content
#     })

# @api_view(['GET'])
# @permission_classes([AllowAny])
# def shared_note(request, note_id):
#     note = get_object_or_404(Note, id=note_id)
#     serializer = NoteSerializer(note)
#     return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def share_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    share, created = Share.objects.get_or_create(note=note)
    
    current_site = get_current_site(request)
    share_url = f"https://{current_site.domain}/shared/{share.token}/"
    
    return Response({
        "share_url": share_url,
        "token": str(share.token),
        "expires": share.expires_at
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def shared_note(request, token):
    share = get_object_or_404(Share, token=token)
    share.accessed_count += 1
    share.save()
    
    return Response({
        "title": share.note.title,
        "content": share.note.content,
        "shared_by": share.note.user.email,
        "access_count": share.accessed_count
    })
# Add this HTML template rendering function
def render_shared_note_html(note, share_url):
    return f"""
    <html>
        <head>
            <title>{note.title}</title>
            <meta property="og:title" content="{note.title}">
            <meta property="og:description" content="{note.content[:200]}">
            <meta property="og:type" content="website">
            <meta property="og:url" content="{share_url}">
        </head>
        <body>
            <h1>{note.title}</h1>
            <p>{note.content}</p>
            <div class="share-buttons">
                <!-- Add social media sharing buttons here -->
            </div>
        </body>
    </html>
    """