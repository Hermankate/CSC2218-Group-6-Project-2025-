from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from .models import Note
from .serializers import NoteSerializer, UserSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Handle user registration with token authentication
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user with hashed password
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        # Create authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    """
    Handle user login and token generation
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response(
                {'error': 'Invalid Credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })

class NoteListCreateView(generics.ListCreateAPIView):
    """
    Handle listing and creating notes for authenticated users
    """
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only the current user's notes
        return Note.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically associate note with current user
        serializer.save(user=self.request.user)

class NoteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handle retrieving, updating, and deleting individual notes
    """
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensure users can only access their own notes
        return Note.objects.filter(user=self.request.user)