from django.urls import path
from django.urls import path
from .views import (
    RegisterView,
    sync_notes,
    NoteListCreateView,
    NoteRetrieveUpdateDestroyView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('sync/', sync_notes, name='sync-notes'),
    path('notes/', NoteListCreateView.as_view(), name='note-list'),
    path('notes/<int:pk>/', NoteRetrieveUpdateDestroyView.as_view(), name='note-detail'),
]