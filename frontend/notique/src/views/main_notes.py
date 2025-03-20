import flet as ft
from src.api import api
from src.utilities import show_snackbar

def main_notes_view(page: ft.Page, refresh_notes):
    BG = "#041955"
    user_name = page.data.get("current_user", {}).get("username", "Guest")
    tasks = ft.ListView(expand=True, spacing=10)
    loading = ft.ProgressBar(visible=False)
    show_sidebar = False

    def build_note_card(note):
        return ft.Container(
            height=60,
            bgcolor=BG,
            border_radius=20,
            padding=15,
            content=ft.Row(
                [
                    ft.Checkbox(
                        label=note["title"],
                        label_style=ft.TextStyle(color="white"),
                        value=False,
                        check_color=ft.colors.WHITE,
                        fill_color=ft.colors.PINK
                    ),
                    ft.IconButton(
                        icon=ft.icons.DELETE,
                        on_click=lambda e, nid=note.get('id', note.get('local_id')): delete_note(nid)
                    )
                ],
                alignment="spaceBetween"
            ),
            on_click=lambda e, nid=note.get('id', note.get('local_id')): page.go(f"/notes?note_id={nid}")
        )

    def load_notes():
        try:
            tasks.controls.clear()
            loading.visible = True
            page.update()

            server_notes = []
            if api.token:
                response = api.get_notes()
                if response and response.status_code == 200:
                    server_notes = response.json()

            local_notes = page.client_storage.get("local_notes") or []
            all_notes = []
            if api.token:  # Logged-in users
                all_notes = server_notes
            else:  # Guest users
                all_notes = [n for n in local_notes if not n.get('synced')]

            for note in all_notes:
                tasks.controls.append(build_note_card(note))

        except Exception as e:
            show_snackbar(page, f"Error loading notes: {str(e)}")
        finally:
            loading.visible = False
            page.update()

    def delete_note(note_id):
        try:
            if isinstance(note_id, int):
                response = api.delete_note(note_id)
                if not response or response.status_code != 204:
                    raise Exception("Server delete failed")
            
            local_notes = page.client_storage.get("local_notes") or []
            local_notes = [n for n in local_notes if n.get('local_id') != note_id]
            page.client_storage.set("local_notes", local_notes)
            
            load_notes()
            [refresh() for refresh in refresh_notes]
            
        except Exception as e:
            show_snackbar(page, f"Delete error: {str(e)}")

    def sync_notes(e):
        try:
            local_notes = page.client_storage.get("local_notes") or []
            if not local_notes:
                show_snackbar(page, "No local notes to sync")
                return

            response = api.sync_notes(
                page.client_storage.get("local_storage_id"),
                local_notes
            )
            
            if response and response.status_code == 200:
                page.client_storage.remove("local_notes")
                data = response.json()
                page.client_storage.set("auth_token", data['token'])
                page.client_storage.set("current_user", data['user'])
                show_snackbar(page, f"Synced {len(local_notes)} notes!")
                load_notes()
            else:
                show_snackbar(page, "Sync failed. Keeping local copy.")
                
        except Exception as e:
            show_snackbar(page, f"Sync error: {str(e)}")

    def toggle_sidebar(e):
        nonlocal show_sidebar
        show_sidebar = not show_sidebar
        sidebar.visible = show_sidebar
        page.update()

    sidebar = ft.Container(
        width=280,
        height=page.height,
        bgcolor=BG,
        padding=20,
        content=ft.Column(
            [
                ft.IconButton(ft.icons.ARROW_BACK, on_click=toggle_sidebar),
                ft.Text(user_name, size=18, weight="bold", color="white"),
                ft.Divider(color="white24"),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.SYNC,color="black"),
                    title=ft.Text("Sync Now",color="white" ),
                    on_click=sync_notes
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.SETTINGS,color="black"),
                    title=ft.Text("Settings",color="white")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.EXIT_TO_APP, color="red"),
                    title=ft.Text("Logout",color="white"),
                    on_click=lambda e: page.go("/logout")
                )
            ],
            spacing=20
        ),
        visible=False
    )

    main_content = ft.Container(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(ft.icons.MENU, on_click=toggle_sidebar),
                        ft.Row([
                            ft.IconButton(ft.icons.SEARCH),
                            ft.IconButton(ft.icons.NOTIFICATIONS_NONE)
                        ])
                    ],
                    alignment="spaceBetween"
                ),
                ft.Text(f"Welcome back, {user_name}!", size=20, weight="bold"),
                ft.Container(
                    height=100,
                    content=ft.ListView(
                        horizontal=True,
                        controls=[
                            ft.Container(
                                width=160,
                                padding=15,
                                bgcolor=BG,
                                border_radius=15,
                                content=ft.Column([
                                    ft.Text("Total Notes", size=12 , color="white"),
                                    ft.Text(str(len(tasks.controls)), size=20, weight="bold", color="white"),
                                    ft.ProgressBar(value=0.7, width=400)
                                ])
                            )
                        ]
                    )
                ),
                ft.Text("Your Notes", size=16),
                        
                                ft.Column([
                                    ft.ListView(
                                        controls=[ft.Container(expand=True, content=tasks),]),
                                     ],    
                                    expand=True,
                                    spacing=20
                                            ),
                                            
            ]

        ) 
          
    )
    fab =ft.FloatingActionButton(
                icon=ft.icons.ADD,
                on_click=lambda e: page.go("/notes"),
                bgcolor=ft.colors.PINK_ACCENT,
                right=20,  # Position from right edge
    bottom=20  # Position from bottom edge
                                                                        )
    
    load_notes()
    refresh_notes.append(load_notes)  # Critical fix for refresh propagation
    return ft.View("/", [ft.Stack([main_content,fab, sidebar]), loading])
