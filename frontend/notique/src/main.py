import flet as ft
from backend.db import init_db, add_note, get_notes, update_note, delete_note, get_note_by_id, add_user


def signup_app(page: ft.Page):
    page.title = "Sign Up"
    page.vertical_alignment = "center"
    
    name_field = ft.TextField(label="Name", width=300)
    email_field = ft.TextField(label="Email", width=300)
    error_text = ft.Text(color="red")
    
    def handle_submit(e):
        if not name_field.value:
            error_text.value = "Please enter your name"
            page.update()
            return
        if not email_field.value or "@" not in email_field.value:
            error_text.value = "Please enter a valid email"
            page.update()
            return
            
        try:
            user_id = add_user(name_field.value, email_field.value)
            page.data["current_user"] = {
                "id": user_id,
                "name": name_field.value,
                "email": email_field.value
            }
            page.go("/")
        except Exception as e:
            error_text.value = str(e)
            page.update()
    
    return ft.View(
        "/signup",
        controls=[
            ft.Column(
                [
                    ft.Text("Welcome! Sign Up", size=24, weight="bold"),
                    name_field,
                    email_field,
                    ft.ElevatedButton("Continue", on_click=handle_submit),
                    error_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )
def todo_app(page: ft.Page, refresh_notes):
    page.title = "Flet Todo Mobile"
    page.window_width = 360
    page.window_height = 640
    page.window_resizable = False

    BG = "#041955" 
    PINK = "white"
    user_name = page.data["current_user"]["name"]

    tasks = ft.ListView(expand=True, spacing=10, padding=ft.padding.only(bottom=20, top=10))
    
    # Create navigation drawer
    drawer = ft.NavigationDrawer(
        controls=[
            ft.Container(height=12),
            ft.NavigationDrawerDestination(
                label="Profile",
                icon=ft.icons.PERSON,  # This should be ft.Icons.PERSON
            ),
            ft.NavigationDrawerDestination(
                label="Settings",
                icon=ft.icons.SETTINGS,  # This should be ft.Icons.SETTINGS
            ),
            ft.NavigationDrawerDestination(
                label="About",
                icon=ft.icons.INFO,  # This should be ft.Icons.INFO
            ),
        ],
    )
    page.drawer = drawer

    def open_drawer(e):
        page.drawer.open = True  # Correct way to open the drawer
        page.update()

    def load_notes():
        tasks.controls.clear()
        for note in get_notes(page.data["current_user"]["id"]):
            note_id = note["id"]
            tasks.controls.append(
                ft.Container(
                    height=60,
                    bgcolor=BG,
                    border_radius=20,
                    padding=ft.padding.symmetric(horizontal=15),
                    content=ft.Row(
                        controls=[
                            ft.Checkbox(
                                label=note["title"],
                                value=False,
                                check_color=ft.Colors.WHITE,
                                fill_color=ft.Colors.PINK,
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                icon_color="red",
                                on_click=lambda e, note_id=note_id: [
                                    delete_note(note_id),
                                    load_notes(),
                                    [refresh() for refresh in refresh_notes]
                                ]
                            )
                        ],
                        alignment="spaceBetween"
                    )
                )
            )
        page.update()

    refresh_notes.append(load_notes)
    load_notes()

    return ft.View(
        "/",
        [
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(ft.icons.MENU, on_click=open_drawer),  # Should be ft.Icons.MENU
                            ft.Row([
                                ft.IconButton(icon=ft.icons.SEARCH),  # Should be ft.Icons.SEARCH
                                ft.IconButton(icon=ft.icons.NOTIFICATIONS)  # Should be ft.Icons.NOTIFICATIONS
                            ])
                        ],
                        alignment="spaceBetween"
                    ),
                    ft.Text(f"What's up, {user_name}!", size=20, weight="bold"),
                    ft.Text("TODAY'S TASKS", size=12, color="white54"),
                    ft.Container(
                        content=tasks,
                        expand=True
                    ),
                    ft.Row(
                        [
                        ft.FloatingActionButton(
                                icon=ft.icons.ADD,  # Should be ft.Icons.ADD
                                on_click=lambda _: page.go("/notes"),
                                bgcolor= "#eb06ff"
                        )
                        ],
                        alignment="end"
                    )
                ],
                expand=True,
                spacing=0
            )
        ]
    )
def notes_app(page: ft.Page, refresh_notes):
    page.title = "Note-Taking App"
    user_id = page.data["current_user"]["id"]

    title_input = ft.TextField(label="Title")
    content_input = ft.TextField(label="Content", multiline=True, min_lines=5)
    notes_list = ft.Column(scroll=ft.ScrollMode.ADAPTIVE)

    def load_notes():
        notes_list.controls.clear()
        for note in get_notes(user_id):
            notes_list.controls.append(
                ft.ListTile(
                    title=ft.Text(note["title"]),
                    subtitle=ft.Text(note["content"]),
                    on_click=lambda e, nid=note["id"]: open_note(nid)
                )
            )
        page.update()

    def save_note(e):
        if title_input.value and content_input.value:
            add_note(user_id, title_input.value, content_input.value)
            title_input.value = ""
            content_input.value = ""
            load_notes()
            page.go("/")

    def open_note(note_id):
        note = get_note_by_id(note_id)
        if note:
            title_input.value = note["title"]
            content_input.value = note["content"]
            page.update()

    return ft.View(
        "/notes",
        [
            ft.AppBar(
                title=ft.Text("Notes"),
                bgcolor=ft.colors.BLUE,
                leading=ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda _: page.go("/")
                )
            ),
            ft.Column(
                [
                    title_input,
                    content_input,
                    ft.Row(
                        [
                            ft.ElevatedButton("Save", on_click=save_note),
                            ft.ElevatedButton("Cancel", on_click=lambda _: page.go("/"))
                        ],
                        spacing=10
                    ),
                    notes_list
                ],
                expand=True,
                scroll=ft.ScrollMode.ADAPTIVE,
    
            )
        ]
    )

def main(page: ft.Page):
    page.data = {}
    refresh_notes = []
    init_db()

    def route_change(e):
        page.views.clear()
        
        if page.route == "/signup":
            view = signup_app(page)
        elif page.route == "/":
            if "current_user" not in page.data:
                page.go("/signup")
                return
            view = todo_app(page,refresh_notes)
        elif page.route == "/notes":
            if "current_user" not in page.data:
                page.go("/signup")
                return
            view = notes_app(page,refresh_notes)
        
        page.views.append(view)
        page.update()

    page.on_route_change = route_change
    page.go("/signup")

ft.app(target=main, view=ft.AppView.FLET_APP)
