import flet as ft
from datetime import datetime
import uuid

def show_snackbar(page: ft.Page, message: str):
    page.snack_bar = ft.SnackBar(ft.Text(message))
    page.snack_bar.open = True
    page.update()

def handle_offline_save(page, note_data):
    local_notes = page.client_storage.get("local_notes") or []
    note_data.update({
        'local_id': str(uuid.uuid4()),
        'created_at': datetime.now().isoformat(),
        'synced': False
    })
    local_notes.append(note_data)
    page.client_storage.set("local_notes", local_notes)
    show_snackbar(page, "Note saved locally")