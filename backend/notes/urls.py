from django.urls import path
from .views import *

from django.urls import path
from .views import get_notes

urlpatterns = [
    path('notes/', get_notes, name='get_notes'),  # This is the endpoint to get all notes
]
