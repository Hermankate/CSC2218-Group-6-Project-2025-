import flet as ft

def note_card(note, open_note, delete_note):
    return ft.ListTile(
        title=ft.Text(note["title"]),
        subtitle=ft.Text(note["content"][:50] + "..."),  # Preview first 50 chars
        on_click=lambda e: open_note(note),
        trailing=ft.IconButton(ft.Icons.DELETE, on_click=lambda e: delete_note(note["id"]))
    )
