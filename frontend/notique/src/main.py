import flet as ft
from backend.db import init_db, add_note, get_notes, update_note, delete_note, get_note_by_id, add_user
def signup_app(page: ft.Page):
    page.title = "Sign Up"
    page.vertical_alignment = "center"
    
    username_field = ft.TextField(label="Username", width=300)
    email_field = ft.TextField(label="Email", width=300)
    password_field = ft.TextField(
        label="Password", 
        password=True, 
        can_reveal_password=True,  # Show/hide toggle
        width=300
    )
    error_text = ft.Text(color="red")
    
    def handle_submit(e):
        # Validate all fields
        if not all([username_field.value, email_field.value, password_field.value]):
            error_text.value = "All fields are required"
            page.update()
            return
            
        try:
            # Send registration request to Django
            response = api.register(
                username=username_field.value,
                email=email_field.value,
                password=password_field.value
            )
            
            if response.status_code == 201:
                data = response.json()
                # Store authentication data
                page.client_storage.set("auth_token", data['token'])
                page.client_storage.set("current_user", data['user'])
                page.data["current_user"] = data['user']
                page.go("/")
            else:
                error_text.value = response.json().get('error', 'Registration failed')
                
        except Exception as e:
            error_text.value = f"Connection error: {str(e)}"
            
        page.update()
    
    return ft.View(
        "/signup",
        controls=[
            ft.Column(
                [
                    ft.Text("Create Account", size=24, weight="bold"),
                    username_field,
                    email_field,
                    password_field,
                    ft.ElevatedButton("Sign Up", on_click=handle_submit),
                    ft.TextButton(
                        "Already have an account? Login",
                        on_click=lambda _: page.go("/login")  # Add login route
                    ),
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
    user_name = page.data["current_user"]["name"]
    
    # Sidebar visibility state
    show_sidebar = False
    # Toggle sidebar function

    def toggle_sidebar(e):
        nonlocal show_sidebar
        sidebar.visible = show_sidebar
        show_sidebar = not show_sidebar
        sidebar.visible = show_sidebar
        page.update()


    # Sidebar (25% width)
    sidebar = ft.Container(
        width=page.width * 0.8,
        bgcolor=BG,
        padding=20,
        content=ft.Column(
            controls=[
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda _: toggle_sidebar),
                
                ft.Column([
                ft.Text(user_name, size=16, weight="bold", color="white"),
                ft.Divider(height=20, color="black"),
                ft.Row([
                ft.Icon(ft.icons.PERSON, color="blue"),
                ft.Text("Profile", color="white"),
                ]), 
                ]),
                ft.Row([
                    ft.Icon(ft.icons.SETTINGS, color="blue"),
                    ft.Text("Settings", color="white"),
                ]),
                ft.Row([
                    ft.Icon(ft.icons.INFO, color="blue"),
                    ft.Text("About", color="white"),
                ]),
            ],
            spacing=20
        )
    )

    
    # Main content area
    tasks = ft.ListView(expand=True, spacing=10, padding=ft.padding.only(bottom=20, top=10))
    
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
                    on_click=lambda e, nid=note_id: page.go(f"/notes?note_id={nid}"),
                    content=ft.Row(
                        controls=[
                            ft.Checkbox(
                                label=note["title"],
                                value=False,
                                check_color=ft.colors.WHITE,
                                fill_color=ft.colors.PINK,
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

    # Categories Card
    categories_card = ft.ListView(horizontal=True, spacing=10, height=100, padding=10)
    categories = ["Business", "Family", "Friends"]
    for category in categories:
        categories_card.controls.append(
            ft.Container(
                width=140,
                height=90,
                bgcolor=BG,
                border_radius=15,
                padding=12,
                content=ft.Column([
                    ft.Text("40 Tasks", size=12,color="white"),
                    ft.Text(category, size=14, color="white") ,
                    ft.Container(
                        height=4,
                        bgcolor="white24",
                        border_radius=2,
                        content=ft.Container(bgcolor="#eb06ff", width=60)
                    )
                ])
            )
        )

    main_content = ft.Container(
        expand=True,
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(ft.icons.MENU, on_click=toggle_sidebar, icon_color="black"),
                        ft.Row([
                            ft.IconButton(ft.icons.SEARCH, icon_color="black"),
                            ft.IconButton(ft.icons.NOTIFICATIONS, icon_color="black")
                        ])
                    ],
                    alignment="spaceBetween"
                ),
                ft.Text(f"What's up, {user_name}!", size=20, weight="bold", color="black"),
                ft.Text("CATEGORIES", size=12, color="black"),
                ft.Container(height=100, content=categories_card),
                ft.Text("TODAY'S TASKS", size=12, color="black"),
                ft.Container(expand=True, content=tasks),
                ft.Row([
                
                ft.FloatingActionButton(
                    icon=ft.icons.ADD,
                    on_click=lambda _: page.go("/notes"),
                    bgcolor="#eb06ff"
                )], alignment= ft.MainAxisAlignment.END
                )
            ],
            expand=True,
            spacing=20
        )
    )

    # Layout with conditional sidebar
    layout = ft.Stack(
    [
        main_content,
        ft.Container(  # Sidebar
            content=sidebar,
            visible=show_sidebar,
            left=0,
            top=0,
            bottom=0,
            width=page.width * 0.5,  # Sidebar width
            bgcolor=BG,
            padding=10,
        ),
    ],
    expand=True
)

    refresh_notes.append(load_notes)
    load_notes()

    return ft.View("/", [layout])

def notes_app(page: ft.Page, refresh_notes):
    page.title = "Note-Taking App"
    user_id = page.data["current_user"]["id"]
    note_id = page.route.split("=")[1] if "note_id" in page.route else None

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
            if note_id:
                update_note(note_id, title_input.value, content_input.value)
            else:
                add_note(user_id, title_input.value, content_input.value)
            title_input.value = ""
            content_input.value = ""
            [refresh() for refresh in refresh_notes]
            page.go("/")

    def open_note(nid):
        note = get_note_by_id(nid)
        if note:
            title_input.value = note["title"]
            content_input.value = note["content"]
            page.update()

    # Load existing note if editing
    if note_id:
        note = get_note_by_id(note_id)
        if note:
            title_input.value = note["title"]
            content_input.value = note["content"]

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
def login_app(page: ft.Page):
    page.title = "Login"
    username_field = ft.TextField(label="Username")
    password_field = ft.TextField(label="Password", password=True)
    error_text = ft.Text(color="red")

    def handle_login(e):
        try:
            response = api.login(
                username_field.value,
                password_field.value
            )
            if response.status_code == 200:
                data = response.json()
                page.client_storage.set("auth_token", data['token'])
                page.client_storage.set("current_user", data['user'])
                page.data["current_user"] = data['user']
                page.go("/")
            else:
                error_text.value = "Invalid credentials"
        except Exception as e:
            error_text.value = f"Login error: {str(e)}"
        page.update()

    return ft.View(
        "/login",
        [
            ft.Column(
                [
                    ft.Text("Login", size=24),
                    username_field,
                    password_field,
                    ft.ElevatedButton("Login", on_click=handle_login),
                    ft.TextButton("Create Account", on_click=lambda _: page.go("/signup")),
                    error_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        ]
    )

def main(page: ft.Page):
    # Initialize page data and API
    page.data = {}
    refresh_notes = []
    
    # Check for existing valid session
    token = page.client_storage.get("auth_token")
    if token:
        try:
            # Set token in API client
            api.set_token(token)
            
            # Verify token validity by making a test request
            notes_response = api.get_notes()
            
            if notes_response.status_code == 200:
                # Load user data from storage
                page.data["current_user"] = page.client_storage.get("current_user")
                page.go("/")  # Redirect to main view
                return
            else:
                # Invalid token, clear storage
                page.client_storage.remove("auth_token")
                page.client_storage.remove("current_user")
                
        except Exception as e:
            # Handle network errors
            print(f"Session validation error: {e}")
            page.client_storage.clear()

    def route_change(e):
        page.views.clear()
        
        # Route handling
        if page.route == "/signup":
            view = signup_app(page)
        elif page.route == "/login":
            view = login_app(page)  # You'll need to implement this
        elif page.route == "/":
            if "current_user" not in page.data:
                page.go("/login")
                return
            view = todo_app(page, refresh_notes)
        elif page.route.startswith("/notes"):
            if "current_user" not in page.data:
                page.go("/login")
                return
            view = notes_app(page, refresh_notes)
        elif page.route == "/logout":
            # Clear session on logout
            page.client_storage.remove("auth_token")
            page.client_storage.remove("current_user")
            page.data.clear()
            page.go("/login")
            return
        
        page.views.append(view)
        page.update()

    # Setup route handlers
    page.on_route_change = route_change
    
    # Initial route - check if we need to redirect
    if "current_user" in page.data:
        page.go("/")
    else:
        page.go("/login" if page.client_storage.get("auth_token") else "/signup")

ft.app(target=main, view=ft.AppView.FLET_APP)