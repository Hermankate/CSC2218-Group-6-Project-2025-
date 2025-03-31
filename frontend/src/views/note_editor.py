import flet as ft
from api import api
from utilities import show_snackbar

def note_editor_view(page: ft.Page, refresh_notes):
    note_id = page.route.split("?note_id=")[-1] if "?note_id=" in page.route else None
    categories = ["Uncategorized", "Business", "Family", "Friends", "Personal"]
    tagged_usernames = []
    
    def handle_content_change(e):
        content = content_field.value
        if not content:
            return
            
        if "@" in content:
            parts = content.rsplit("@", 1)
            query = parts[-1].strip()
            search_users(query)
        else:
            users_search.visible = False
            page.update()

    def search_users(query):
        try:
            if api.token:
                response = api.search_users(query)
                if response and response.status_code == 200:
                    users = response.json()
                    users_search.controls = [
                        ft.ListTile(
                            title=ft.Text(user['username']),
                            subtitle=ft.Text(user['email']),
                            on_click=lambda e, u=user: select_user(u),
                        ) for user in users
                    ]
                    users_search.visible = True
                    page.update()
        except Exception as e:
            show_snackbar(page, f"Error searching users: {str(e)}")

    def select_user(user):
        current_content = content_field.value
        new_content = current_content.rsplit("@", 1)[0] + f"@{user['username']} "
        content_field.value = new_content
        tagged_usernames.append(user['username'])
        users_search.visible = False
        page.update()

    users_search = ft.Column(
        visible=False,
        scroll=ft.ScrollMode.ALWAYS,
        height=150
    )

    category_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(c) for c in categories],
        value="Uncategorized",
        width=150,
    )
    
    title_field = ft.TextField(
        label="Title", 
        autofocus=True,
        hint_text="Enter note title"
    )
    
    content_field = ft.TextField(
        label="Content (use @ to tag users)",
        multiline=True,
        expand=True,
        on_change=handle_content_change
    )
    
    error_text = ft.Text(color="red")
    loading = ft.ProgressBar(visible=False)

    def load_existing_note():
        try:
            if note_id:
                if api.token:
                    response = api.get_note(note_id)
                    if response and response.status_code == 200:
                        note = response.json()
                        title_field.value = note.get("title", "")
                        content_field.value = note.get("content", "")
                        category_dropdown.value = note.get("category", "Uncategorized")
                        tagged_usernames.extend(note.get("tagged_usernames", []))
                else:
                    local_notes = page.client_storage.get("local_notes") or []
                    note = next((n for n in local_notes if str(n.get("local_id")) == note_id), None)
                    if note:
                        title_field.value = note.get("title", "")
                        content_field.value = note.get("content", "")
                        category_dropdown.value = note.get("category", "Uncategorized")
                        tagged_usernames.extend(note.get("tagged_usernames", []))
        except Exception as e:
            show_snackbar(page, f"Error loading note: {str(e)}")

    load_existing_note()

    def save_note(e):
        error_text.value = ""
        title = title_field.value.strip()
        content = content_field.value.strip()
        category = category_dropdown.value

        if not title:
            error_text.value = "Title is required"
            page.update()
            return

        try:
            loading.visible = True
            page.update()
            
            note_data = {
                "title": title,
                "content": content,
                "category": category,
                "tagged_usernames": list(set(tagged_usernames))
            }
            
            if api.token:
                if note_id:
                    response = api.update_note(note_id, note_data)
                else:
                    response = api.create_note(note_data)
                
                if response and response.status_code in [200, 201]:
                    show_snackbar(page, "Note saved successfully!")
            else:
                local_notes = page.client_storage.get("local_notes") or []
                if note_id:
                    note_index = next((i for i, n in enumerate(local_notes) 
                                    if str(n.get("local_id")) == note_id), None)
                    if note_index is not None:
                        local_notes[note_index] = {
                            **local_notes[note_index],
                            **note_data,
                            "local_id": note_id
                        }
                else:
                    local_notes.append({
                        **note_data,
                        "local_id": api.local_id,
                        "synced": False
                    })
                page.client_storage.set("local_notes", local_notes)
                show_snackbar(page, "Note saved locally!")
            
            for refresh in refresh_notes:
                refresh()
            page.go("/")

        except Exception as e:
            error_text.value = f"Error: {str(e)}"
        finally:
            loading.visible = False
            page.update()

    return ft.View(
        "/notes",
        [
            ft.AppBar(
                title=ft.Text("Edit Note" if note_id else "New Note"),
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: page.go("/")
                )
            ),
            ft.Column(
                [
                    title_field,
                    ft.Row([
                        ft.Text("Category:", color="white"),
                        category_dropdown
                    ], alignment="start"),
                    content_field,
                    users_search,
                    ft.Row([
                        ft.ElevatedButton("Save", on_click=save_note),
                        ft.TextButton("Cancel", on_click=lambda e: page.go("/"))
                    ], spacing=20)
                ],
                expand=True,
                spacing=20
            ),
            loading,
            error_text
        ]
    )

