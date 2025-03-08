import flet as ft

def main(page: ft.Page):
    page.title = "Note-Taking App"
    page.window_width = 500
    page.window_height = 700

    title_field = ft.TextField(label="Title")
    content_field = ft.TextField(label="Content", multiline=True, min_lines=5)

    notes_list = ft.Column()

    def load_notes():
        notes_list.controls.clear()
        for note in get_notes():
            note_id, title, content = note
            notes_list.controls.append(
                ft.ListTile(
                    title=ft.Text(title),
                    subtitle=ft.Text(content[:30] + "..."),
                    on_click=lambda e, id=note_id, t=title, c=content: open_note(id, t, c)
                )
            )
        page.update()

    def open_note(note_id, title, content):
        title_field.value = title
        content_field.value = content
        page.update()

        def save_edits(e):
            update_note(note_id, title_field.value, content_field.value)
            load_notes()

        def delete_this_note(e):
            delete_note(note_id)
            load_notes()

        page.dialog = ft.AlertDialog(
            title=ft.Text("Edit Note"),
            content=ft.Column([title_field, content_field]),
            actions=[
                ft.TextButton("Save", on_click=save_edits),
                ft.TextButton("Delete", on_click=delete_this_note)
            ]
        )
        page.dialog.open = True
        page.update()

    def save_note(e):
        add_note(title_field.value, content_field.value)
        title_field.value = ""
        content_field.value = ""
        load_notes()

    page.add(
        ft.Column([
            title_field,
            content_field,
            ft.ElevatedButton("Save Note", on_click=save_note),
            ft.Text("Saved Notes"),
            notes_list
        ])
    )

    load_notes()

ft.app(target=main)
