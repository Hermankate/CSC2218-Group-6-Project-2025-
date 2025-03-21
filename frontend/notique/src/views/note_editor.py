from datetime import datetime
import uuid
import flet as ft
from api import api
from utilities import show_snackbar, handle_offline_save

def note_editor(page: ft.Page, refresh_notes):
    title_input = ft.TextField(label="Title", autofocus=True)
    content_input = ft.TextField(label="Content", multiline=True, min_lines=5)
    error_text = ft.Text(color="red")
    loading = ft.ProgressBar(visible=False)
    note_id = page.route.split("=")[-1] if "note_id" in page.route else None

    def load_note():
        if note_id:
            try:
                response = api.get_notes()
                if response and response.status_code == 200:
                    notes = response.json()
                    note = next((n for n in notes if str(n['id']) == note_id), None)
                    if note:
                        title_input.value = note['title']
                        content_input.value = note['content']
                        page.update()
            except:
                show_snackbar(page, "Error loading note")

    def save_note(e):
        title = title_input.value.strip()
        content = content_input.value.strip()

        if not title:
            error_text.value = "Title is required"
            return page.update()

        try:
            loading.visible = True
            page.update()

            note_data = {'title': title, 'content': content}
            if note_id and note_id.isdigit():
                response = api.update_note(note_id, **note_data)
            else:
                response = api.create_note(**note_data)
                page.go("/")

            if response and response.status_code in [200, 201]:
                [refresh() for refresh in refresh_notes]
                page.go("/")
            else:
                handle_offline_save(note_data)
                page.go("/")

        except Exception as e:
            show_snackbar(page, f"Error: {str(e)}")
        finally:
            loading.visible = False
            page.update()

    def handle_offline_save(note_data):
        local_notes = page.client_storage.get("local_notes") or []
        note_data.update({
            'local_id': str(uuid.uuid4()),
            'created_at': datetime.now().isoformat(),
            'synced': False
        })
        local_notes.append(note_data)
        page.client_storage.set("local_notes", local_notes)
        show_snackbar(page, "Note saved locally")

    load_note()
    return ft.View(
        "/notes",
        [
            ft.AppBar(
                title=ft.Text("Note Editor"),
                bgcolor=ft.colors.BLUE_700,
                leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: page.go("/"))
            ),
            ft.Container(
                padding=20,
                content=ft.Column(
                    [
                        title_input,
                        content_input,
                        ft.Row(
                            [
                                ft.ElevatedButton("Save", on_click=save_note),
                                ft.OutlinedButton("Cancel", on_click=lambda e: page.go("/"))
                            ],
                            spacing=20
                        ),
                        error_text,
                        loading
                    ],
                    expand=True,
                    scroll=ft.ScrollMode.ADAPTIVE
                )
            )
        ]
    )
