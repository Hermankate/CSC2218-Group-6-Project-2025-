import flet as ft
from backend.db import init_db, add_note, get_notes, update_note, delete_note, get_note_by_id  # Ensure get_note_by_id exists
from frontend.ui import note_card

def todo_app(page: ft.Page, refresh_notes):
    page.title = "Flet Todo Mobile"
    page.window_width = 360
    page.window_height = 640
    page.window_resizable = False
    page.padding = 0
    page.spacing = 0

    BG = "#041955"
    PINK = "#eb06ff"

    tasks = ft.ListView(expand=True, spacing=10, padding=ft.padding.only(bottom=20, top=10))

    def load_notes():
        tasks.controls.clear()
        for note in get_notes():
            note_id = note["id"]
            tasks.controls.append(
                ft.Container(
                    height=60,
                    bgcolor=BG,
                    border_radius=20,
                    padding=ft.padding.only(left=15, top=15),
                    content=ft.Checkbox(
                        label=note["title"],
                        value=False,
                        check_color=ft.Colors.WHITE,
                        fill_color=ft.Colors.PINK,
                        hover_color=ft.Colors.PINK_100,
                    ),
                    on_click=lambda e, note_id=note_id: [
                        page.data.update({"editing_note_id": note_id}),
                        page.go("/notes")
                    ]
                )
            )
        page.update()

    refresh_notes.append(load_notes)
    load_notes()

    main_content = ft.Column(
        expand=True,
        controls=[
            ft.Row(
                alignment="spaceBetween",
                controls=[
                    ft.IconButton(icon=ft.Icons.MENU),
                    ft.Row([ft.IconButton(icon=ft.Icons.SEARCH), ft.IconButton(icon=ft.Icons.NOTIFICATIONS)]),
                ]
            ),
            ft.Text("What's up, Olivia!", size=20, weight="bold"),
            ft.Text("TODAY'S TASKS", size=12, color="white54"),
            ft.Container(expand=True, content=tasks),
            ft.FloatingActionButton(
                icon=ft.Icons.ADD,
                on_click=lambda _: page.go("/notes"),
                bgcolor=PINK
            ),
        ]
    )

    return ft.View("/", [main_content])

def notes_app(page: ft.Page, refresh_notes):
    page.title = "Note-Taking App"
    page.scroll = "adaptive"

    def go_back(e):
        page.go("/")  

    title_input = ft.TextField(label="Title")
    content_input = ft.TextField(label="Content", multiline=True, min_lines=5)
    tag_input = ft.TextField(label="Tags (comma-separated)")
    notes_list = ft.Column()

    save_button = ft.ElevatedButton("Save", on_click=lambda e: save_note())
    update_button = ft.ElevatedButton("Update", on_click=lambda e: update_existing_note(), visible=False)

    page.appbar = ft.AppBar(
        leading=ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_back, icon_color=ft.Colors.WHITE),
        title=ft.Text("Notes", color=ft.Colors.WHITE),
        center_title=True,
        bgcolor=ft.Colors.BLUE
    )

    def load_notes():
        notes_list.controls.clear()
        for note in get_notes():
            notes_list.controls.append(note_card(note, open_note, delete_note_handler))
        page.update()

    def save_note():
        if title_input.value and content_input.value:
            add_note(title_input.value, content_input.value)
            title_input.value = ""
            content_input.value = ""
            tag_input.value = ""
            load_notes()
            for refresh in refresh_notes:
                refresh()
            page.update()

    def open_note(note):
        title_input.value = note["title"]
        content_input.value = note["content"]
        tag_input.value = ", ".join(note.get("tags", []))
        save_button.visible = False
        update_button.visible = True
        page.data["current_note_id"] = note["id"]
        page.update()

    def update_existing_note():
        note_id = page.data.get("current_note_id")
        if note_id:
            update_note(note_id, title_input.value, content_input.value)
            title_input.value = ""
            content_input.value = ""
            tag_input.value = ""
            save_button.visible = True
            update_button.visible = False
            page.data.pop("current_note_id", None)
            load_notes()
            for refresh in refresh_notes:
                refresh()
            page.update()

    def delete_note_handler(note_id):
        delete_note(note_id)
        load_notes()
        for refresh in refresh_notes:
            refresh()
        page.update()

    # Check if editing a note from todo_app
    editing_note_id = page.data.pop("editing_note_id", None)
    if editing_note_id:
        note = get_note_by_id(editing_note_id)
        if note:
            open_note(note)

    note_view = ft.Column(
        controls=[title_input, content_input, tag_input, save_button, update_button, notes_list]
    )

    init_db()
    load_notes()

    return ft.View("/notes", [note_view])

def main(page: ft.Page):
    page.data = {}
    refresh_notes = []

    def route_change(route):
        page.views.clear()
        if route.route == "/":
            page.views.append(todo_app(page, refresh_notes))
        elif route.route == "/notes":
            page.views.append(notes_app(page, refresh_notes))
        page.update()

    page.on_route_change = route_change
    page.go("/")

ft.app(target=main, view=ft.AppView.FLET_APP)