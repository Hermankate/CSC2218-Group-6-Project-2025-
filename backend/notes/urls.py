from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    NoteListCreateView,
    NoteRetrieveUpdateDestroyView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('notes/', NoteListCreateView.as_view(), name='note-list'),
    path('notes/<int:pk>/', NoteRetrieveUpdateDestroyView.as_view(), name='note-detail'),
]