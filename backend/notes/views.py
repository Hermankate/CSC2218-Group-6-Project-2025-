from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Note
from .serializers import NoteSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Note
from .serializers import NoteSerializer

@api_view(['GET', 'POST'])
def get_notes(request):
    if request.method == 'GET':
        # Fetch all notes from the database and return them
        notes = Note.objects.all()
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Create a new note and save it in the database
        title = request.data.get("title", "")
        if title:
            note = Note.objects.create(title=title)
            serializer = NoteSerializer(note)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Title is required."}, status=status.HTTP_400_BAD_REQUEST)
