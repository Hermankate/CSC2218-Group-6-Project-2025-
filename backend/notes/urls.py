from django.urls import path
from django.urls import path
from .views import register, share_note, shared_note, sync_notes, NoteListCreateView, NoteRetrieveUpdateDestroyView

from django.urls import path
from .views import register, sync_notes, NoteListCreateView, NoteRetrieveUpdateDestroyView
from .views import CustomAuthToken
from notes import views 
urlpatterns = [
    path('register/', register, name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
    path('sync/', sync_notes, name='sync_notes'),
    #path('api/notes/<int:note_id>/share/', views.share_note),
    path(
        'notes/<int:note_id>/share/',
        share_note,
        name='share-note'
    ),
    path(
        'shared/<uuid:token>/',  # Changed from note_id to token
        shared_note,
        name='shared-note'
    ),
    path('notes/', NoteListCreateView.as_view(), name='note-list-create'),
    path('notes/<int:pk>/', NoteRetrieveUpdateDestroyView.as_view(), name='note-retrieve-update-destroy'),
]