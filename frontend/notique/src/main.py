import flet as ft
import httpx

def main(page: ft.Page):
    page.title = "Notique - Notes App"
    notes_list = ft.Column()  # A container for notes
    note_input = ft.TextField(label="New Note", autofocus=True)  # Input for new notes
    add_note_button = ft.ElevatedButton("Add Note", on_click=lambda e: add_note())  # Button to add note

    # Function to fetch notes from the Django API
    def fetch_notes():
        response = httpx.get("https://notique-backend.onrender.com/api/notes/",timeout=30)  # Send GET request to Django
        if response.status_code == 200:
            notes = response.json()  # Get the notes data in JSON format
            notes_list.controls.clear()  # Clear the list of notes (if any)
            
            # Loop through each note and add it to the UI
            for note in notes:
                notes_list.controls.append(ft.Text(note["title"]))  # Display the title of the note
            page.update()  # Update the UI to reflect the new list of notes

    # Function to add a new note by sending a POST request to the Django API
    def add_note():
        new_note = note_input.value.strip()
        if new_note:
            # Send a POST request with the new note title as JSON
            response = httpx.post(
                "https://notique-backend.onrender.com/api/notes/", 
                json={"title": new_note}  # Proper JSON format
            )
            if response.status_code == 201:  # Check if note was successfully created
                fetch_notes()  # Reload the notes list after adding a new note
                note_input.value = ""  # Clear the input field
                page.update()  # Update the page to reflect the changes
            else:
                print(f"Error: {response.status_code}, {response.text}")

    # Add the UI components
    page.add(ft.Text("Your Notes"), notes_list, note_input, add_note_button)
    fetch_notes()  # Call the function to load notes on app startup

# Run the Flet app
#ft.app(target=main)
ft.app(target=main, view=ft.WEB_BROWSER)

