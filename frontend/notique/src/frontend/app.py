
import flet as ft
from backend.db import init_db, add_note, get_notes, update_note, delete_note
from frontend.ui import note_card

def main(page: ft.Page):
    page.title = "Notique"
    page.scroll = "adaptive"

    # Text fields for note input
    title_input = ft.TextField(label="Title")
    content_input = ft.TextField(label="Content", multiline=True, min_lines=5)
    notes_list = ft.Column()

    # Buttons for saving and updating notes
    save_button = ft.ElevatedButton("Save", on_click=lambda e: save_note())
    update_button = ft.ElevatedButton("Update", on_click=lambda e: update_existing_note(), visible=False)

    # Handle back button logic
    def go_back(e):
        """Reset to 'Create' mode when the back button is pressed."""
        title_input.value = ""
        content_input.value = ""
        save_button.visible = True
        update_button.visible = False
        page.update()

    # Function to toggle the drawer
    def toggle_drawer(e):
        page.drawer.open = not page.drawer.open
        page.update()

    # AppBar with Back Button and Drawer Toggle
    page.appbar = ft.AppBar(
        leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_back),  # Back button
        title=ft.Text("Notes"),
        center_title=True,
        bgcolor=ft.colors.BLUE,
        actions=[
            ft.IconButton(ft.Icons.MENU, on_click=toggle_drawer)  # Menu button
        ]
    )

    # Drawer with Upload, Sharing, and Tagging buttons
    page.drawer = ft.NavigationDrawer(
        controls=[
            ft.ListTile(
                leading=ft.Icon(ft.Icons.UPLOAD),
                title=ft.Text("Upload"),
                on_click=lambda e: print("Upload clicked")
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.SHARE),
                title=ft.Text("Share"),
                on_click=lambda e: print("Share clicked")
            ),
            ft.ListTile(
                leading=ft.Icon(ft.Icons.TAG),
                title=ft.Text("Tag"),
                on_click=lambda e: print("Tagging clicked")
            )
        ]
    )

    # Function to load and display notes
    def load_notes():
        """Fetch notes from the database and display them."""
        notes_list.controls.clear()
        for note in get_notes():
            notes_list.controls.append(note_card(note, open_note, delete_note_handler))
        page.update()

    def save_note():
        """Save a new note."""
        if title_input.value and content_input.value:
            add_note(title_input.value, content_input.value)
            title_input.value = ""
            content_input.value = ""
            load_notes()
            page.update()

    def open_note(note):
        """Open a note for editing."""
        title_input.value = note["title"]
        content_input.value = note["content"]
        save_button.visible = False
        update_button.visible = True
        page.update()

    def update_existing_note():
        """Update an existing note."""
        # Replace with actual logic to get the selected note's ID
        note_id = 1  # Dummy ID; replace with real ID
        update_note(note_id, title_input.value, content_input.value)
        title_input.value = ""
        content_input.value = ""
        save_button.visible = True
        update_button.visible = False
        load_notes()
        page.update()

    def delete_note_handler(note_id):
        """Delete a note from the database and update UI immediately."""
        delete_note(note_id)
        load_notes()
        page.update()

    # Initial view setup
    page.add(
        title_input,
        content_input,
        save_button,
        update_button,
        notes_list
    )

    init_db()  # Initialize database on startup
    load_notes()  # Load existing notes

ft.app(target=main)
