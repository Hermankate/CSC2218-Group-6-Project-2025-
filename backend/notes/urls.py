from django.urls import path
from .views import *

from django.urls import path
from .views import get_notes

from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    NoteListCreateView,
    NoteRetrieveUpdateDestroyView
)

urlpatterns = [
    path('api/users/register/', RegisterView.as_view(), name='register'),
    path('api/users/login/', LoginView.as_view(), name='login'),
    path('api/notes/', NoteListCreateView.as_view(), name='note-list'),
    path('api/notes/<int:pk>/', NoteRetrieveUpdateDestroyView.as_view(), name='note-detail'),
]