from django.urls import path
from django.urls import path
from .views import register, sync_notes, NoteListCreateView, NoteRetrieveUpdateDestroyView

from django.urls import path
from .views import register, sync_notes, NoteListCreateView, NoteRetrieveUpdateDestroyView

urlpatterns = [
    path('register/', register, name='register'),
    path('sync/', sync_notes, name='sync_notes'),
    path('notes/', NoteListCreateView.as_view(), name='note-list-create'),
    path('notes/<int:pk>/', NoteRetrieveUpdateDestroyView.as_view(), name='note-retrieve-update-destroy'),
]