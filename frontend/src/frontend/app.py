from flet import *

def main(page: Page):
    page.title = "Flet Todo Mobile"
    page.window_width = 360
    page.window_height = 640
    page.window_resizable = False
    page.padding = 0
    page.spacing = 0

    BG = "#041955"
    FWG = "#97b4ff"
    FG = "#3450a1"
    PINK = "#eb06ff"

    # Mobile-optimized circle avatar
    circle = Container(
        width=80,
        height=80,
        border_radius=40,
        content=CircleAvatar(
            foreground_image_src="https://images.unsplash.com/photo-1545912452-8aea7e25a3d3?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=687&q=80",
        ),
        bgcolor=BG,
        padding=3,
    )

    def handle_checkbox_change(e):
        # This will automatically update the checkbox state
        print(f"Checkbox value: {e.control.value}")
        # If you need to update other parts of UI:
        page.update()

    def shrink(e):
        page_2.width = page.width * 0.2
        page_2.scale = transform.Scale(0.7, alignment=alignment.center_right)
        page_2.border_radius = border_radius.only(
            top_left=35, top_right=35, bottom_left=35, bottom_right=35
        )
        page.update()

    def restore(e):
        page_2.width = page.width * 1
        page_2.scale = transform.Scale(1, alignment=alignment.center_right)
        page_2.border_radius = 35
        page.update()

    create_task_view = Container(
        content=IconButton(icon=Icons.CLOSE, on_click=lambda _: page.go("/"))
    )

    # Mobile-optimized tasks list
    tasks = ListView(expand=True, spacing=10, padding=padding.only(bottom=20, top=10))
    
    for i in range(10):
        tasks.controls.append(
            Container(
                height=60,
                bgcolor=BG,
                border_radius=20,
                padding=padding.only(left=15, top=15),
                content=Checkbox(
                            label="My Task",
                            value=False,  # Initial state
                            on_change=handle_checkbox_change,
                            check_color=colors.WHITE,  # Tick color
                            fill_color=colors.PINK,    # Background when checked
                            hover_color=colors.PINK_100,
                        )
            )
        )

    # Mobile categories
    categories_card = ListView(horizontal=True, spacing=10, height=100, padding=10)
    
    categories = ["Business", "Family", "Friends"]
    for i, category in enumerate(categories):
        categories_card.controls.append(
            Container(
                width=140,
                height=90,
                bgcolor=BG,
                border_radius=15,
                padding=12,
                content=Column([
                    Text("40 Tasks", size=12),
                    Text(category, size=14),
                    Container(
                        height=4,
                        bgcolor="white24",
                        border_radius=2,
                        content=Container(bgcolor=PINK, width=60)
                    )
                ])
            )
        )

    # Main content column
    main_content = Column(
        expand=True,
        controls=[
            Row(
                alignment="spaceBetween",
                controls=[
                    IconButton(icon=Icons.MENU, on_click=shrink),
                    Row([
                        IconButton(icon=Icons.SEARCH),
                        IconButton(icon=Icons.NOTIFICATIONS)
                    ])
                ]
            ),
            Text("What's up, Olivia!", size=20, weight="bold"),
            Text("CATEGORIES", size=12, color="white54"),
            Container(height=100, content=categories_card),
            Text("TODAY'S TASKS", size=12, color="white54"),
            Container(expand=True, content=tasks),
            FloatingActionButton(
                icon=Icons.ADD,
                on_click=lambda _: page.go("/create_task"),
                bgcolor=PINK
            )
        ]
    )

    # Sidebar (page_1)
    sidebar = Container(
        width=page.width * 0.8,
        bgcolor=BG,
        padding=padding.only(top=40, left=20, right=20),
        content=Column([
            IconButton(icon=Icons.ARROW_BACK, on_click=restore),
            circle,
            Text("Olivia Mitchel", size=20, weight="bold"),
            Divider(height=20, color="white24"),
            Column([
                ListTile(
                    leading=Icon(Icons.FAVORITE_BORDER),
                    title=Text("Favorites", size=14)
                ),
                ListTile(
                    leading=Icon(Icons.WORK_OUTLINE),
                    title=Text("Projects", size=14)
                ),
                ListTile(
                    leading=Icon(Icons.BAR_CHART),
                    title=Text("Statistics", size=14)
                ),
            ], spacing=10),
            Container(expand=True),
            Column([
                Text("Good", color=FWG),
                Text("Consistency", size=16)
            ])
        ])
    )

    # Main content container (page_2)
    page_2 = Container(
        width=page.width * 0.8,
        bgcolor=FG,
        border_radius=35,
        padding=20,
        content=main_content,
        animate=animation.Animation(400, "decelerate"),
    )

    # Mobile layout
    layout = Stack(
        expand=True,
        controls=[
            Container(bgcolor=BG),
            sidebar,
            page_2
        ]
    )

    pages = {
        "/": View("/", [layout]),
        "/create_task": View("/create_task", [
            Container(
                padding=20,
                content=Column([
                    AppBar(title=Text("New Task")),
                    TextField(label="Task title"),
                    ElevatedButton("Create Task")
                ])
            )
        ])
    }

    def route_change(route):
        page.views.clear()
        page.views.append(pages[route.route])
        page.update()

    page.on_route_change = route_change
    page.go(page.route)

app(target=main, view=FLET_APP, assets_dir="assets")