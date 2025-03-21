# from datetime import datetime
# import uuid
# import flet as ft
# from api import api
# from utilities import show_snackbar, handle_offline_save

# def note_editor(page: ft.Page, refresh_notes):
#     title_input = ft.TextField(label="Title", autofocus=True)
#     content_input = ft.TextField(label="Content", multiline=True, min_lines=5)
#     error_text = ft.Text(color="red")
#     loading = ft.ProgressBar(visible=False)
#     note_id = page.route.split("=")[-1] if "note_id" in page.route else None

#     def load_note():
#         if note_id:
#             try:
#                 response = api.get_notes()
#                 if response and response.status_code == 200:
#                     notes = response.json()
#                     note = next((n for n in notes if str(n['id']) == note_id), None)
#                     if note:
#                         title_input.value = note['title']
#                         content_input.value = note['content']
#                         page.update()
#             except:
#                 show_snackbar(page, "Error loading note")

#     def save_note(e):
#         title = title_input.value.strip()
#         content = content_input.value.strip()

#         if not title:
#             error_text.value = "Title is required"
#             return page.update()

#         try:
#             loading.visible = True
#             page.update()

#             note_data = {'title': title, 'content': content}
#             if note_id and note_id.isdigit():
#                 response = api.update_note(note_id, **note_data)
#             else:
#                 response = api.create_note(**note_data)
#                 page.go("/")

#             if response and response.status_code in [200, 201]:
#                 [refresh() for refresh in refresh_notes]
#                 page.go("/")
#             else:
#                 handle_offline_save(note_data)
#                 page.go("/")

#         except Exception as e:
#             show_snackbar(page, f"Error: {str(e)}")
#         finally:
#             loading.visible = False
#             page.update()

#     def handle_offline_save(note_data):
#         local_notes = page.client_storage.get("local_notes") or []
#         note_data.update({
#             'local_id': str(uuid.uuid4()),
#             'created_at': datetime.now().isoformat(),
#             'synced': False
#         })
#         local_notes.append(note_data)
#         page.client_storage.set("local_notes", local_notes)
#         show_snackbar(page, "Note saved locally")

#     load_note()
#     return ft.View(
#         "/notes",
#         [
#             ft.AppBar(
#                 title=ft.Text("Note Editor"),
#                 bgcolor=ft.colors.BLUE_700,
#                 leading=ft.IconButton(ft.icons.ARROW_BACK, on_click=lambda e: page.go("/"))
#             ),
#             ft.Container(
#                 padding=20,
#                 content=ft.Column(
#                     [
#                         title_input,
#                         content_input,
#                         ft.Row(
#                             [
#                                 ft.ElevatedButton("Save", on_click=save_note),
#                                 ft.OutlinedButton("Cancel", on_click=lambda e: page.go("/"))
#                             ],
#                             spacing=20
#                         ),
#                         error_text,
#                         loading
#                     ],
#                     expand=True,
#                     scroll=ft.ScrollMode.ADAPTIVE
#                 )
#             )
#         ]
#     )
#########################################################
# import flet as ft
# from api import api
# from utilities import show_snackbar

# import flet as ft
# from api import api
# from utilities import show_snackbar

# def note_editor_view(page: ft.Page, refresh_notes):
#     categories = ["Uncategorized", "Business", "Family", "Friends", "Personal"]
    
#     category_dropdown = ft.Dropdown(
#         options=[ft.dropdown.Option(c) for c in categories],
#         value="Uncategorized",
#         width=150,
#     )
    
#     title_field = ft.TextField(label="Title", autofocus=True)
#     content_field = ft.TextField(label="Content", multiline=True, expand=True)
#     error_text = ft.Text(color="red")
#     loading = ft.ProgressBar(visible=False)

#     def save_note(e):
#         error_text.value = ""
#         title = title_field.value.strip()
#         content = content_field.value.strip()
#         category = category_dropdown.value

#         if not title:
#             error_text.value = "Title is required"
#             page.update()
#             return

#         try:
#             loading.visible = True
#             page.update()
            
#             note_data = {
#                 "title": title,
#                 "content": content,
#                 "category": category
#             }
            
#             if api.token:
#                 response = api.create_note(note_data)
#                 if response and response.status_code == 201:
#                     show_snackbar(page, "Note saved!")
#             else:
#                 local_notes = page.client_storage.get("local_notes") or []
#                 local_notes.append({
#                     **note_data,
#                     "local_id": len(local_notes) + 1,
#                     "synced": False
#                 })
#                 page.client_storage.set("local_notes", local_notes)
#                 show_snackbar(page, "Note saved locally!")
            
#             # Fixed: Call each refresh function in the list
#             for refresh in refresh_notes:
#                 refresh()
                
#             page.go("/")

#         except Exception as e:
#             error_text.value = f"Error: {str(e)}"
#         finally:
#             loading.visible = False
#             page.update()

#     return ft.View(
#         "/notes",
#         [
#             ft.AppBar(title=ft.Text("Edit Note")),
#             ft.Column([
#                 title_field,
#                 ft.Row([
#                     ft.Text("Category:", color="white"),
#                     category_dropdown
#                 ], alignment="start"),
#                 content_field,
#                 ft.ElevatedButton("Save", on_click=save_note)
#             ], expand=True, spacing=20),
#             loading,
#             error_text
#         ]
#     )


import flet as ft
from api import api
from utilities import show_snackbar

def note_editor_view(page: ft.Page, refresh_notes):
    note_id = page.route.split("?note_id=")[-1] if "?note_id=" in page.route else None
    categories = ["Uncategorized", "Business", "Family", "Friends", "Personal"]
    
    # Form fields
    category_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option(c) for c in categories],
        value="Uncategorized",
        width=150,
    )
    title_field = ft.TextField(label="Title", autofocus=True)
    content_field = ft.TextField(label="Content", multiline=True, expand=True)
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
                else:
                    local_notes = page.client_storage.get("local_notes") or []
                    note = next((n for n in local_notes if str(n.get("local_id")) == note_id), None)
                    if note:
                        title_field.value = note.get("title", "")
                        content_field.value = note.get("content", "")
                        category_dropdown.value = note.get("category", "Uncategorized")
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
                "category": category
            }
            
            if api.token:
                if note_id:
                    response = api.update_note(note_id, note_data)
                else:
                    response = api.create_note(note_data)
                
                if response and response.status_code in [200, 201]:
                    show_snackbar(page, "Note saved!")
            else:
                local_notes = page.client_storage.get("local_notes") or []
                if note_id:
                    # Update existing local note
                    note_index = next((i for i, n in enumerate(local_notes) 
                                    if str(n.get("local_id")) == note_id), None)
                    if note_index is not None:
                        local_notes[note_index] = {
                            **local_notes[note_index],
                            **note_data
                        }
                else:
                    # Create new local note
                    local_notes.append({
                        **note_data,
                        "local_id": len(local_notes) + 1,
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

    def cancel_edit(e):
        page.go("/")

    return ft.View(
        "/notes",
        [
            ft.AppBar(
                title=ft.Text("Edit Note" if note_id else "New Note"),
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=cancel_edit
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
                    ft.Row([
                        ft.ElevatedButton("Save", on_click=save_note),
                        ft.TextButton("Cancel", on_click=cancel_edit)
                    ], spacing=20)
                ],
                expand=True,
                spacing=20
            ),
            loading,
            error_text
        ]
    )