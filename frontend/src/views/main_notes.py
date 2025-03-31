import flet as ft
from api import api
from utilities import show_snackbar

def main_notes_view(page: ft.Page, refresh_notes):
    BG = "#041955"
    PINK = ft.colors.PINK_ACCENT
    user_name = (page.client_storage.get("current_user") or {}).get("username", "Guest")
    tasks = ft.ListView(expand=True, spacing=10)
    loading = ft.ProgressBar(visible=False)
    show_sidebar = False
    all_notes_data = []
    categories = ["All", "Business", "Family", "Friends", "Personal", "Tagged"]
    selected_category = ft.Ref[ft.Text]()
    selected_category.current = ft.Text("All")

    # UI Elements
    search_field = ft.TextField(
        hint_text="Search notes...",
        on_change=lambda e: filter_notes(),
        visible=False,
        expand=True,
        height=40,
        text_size=14,
        border_color="transparent",
        content_padding=5,
    )

    close_search_btn = ft.IconButton(
        ft.icons.CLOSE,
        on_click=lambda e: close_search(),
        visible=False,
    )

    search_icon = ft.IconButton(
        ft.icons.SEARCH,
        on_click=lambda e: open_search(),
    )

    # Category Cards
    categories_card = ft.ListView(
        horizontal=True,
        spacing=10,
        height=100,
    )

    def update_categories():
        categories_card.controls.clear()
        for cat in categories:
            count = len([
                n for n in all_notes_data 
                if (n.get("category") == cat) or 
                (cat == "All") or
                (cat == "Tagged" and any(
                    u['id'] == (page.client_storage.get("current_user") or {}).get('id')
                    for u in n.get('tagged_users', [])
                ))
            ])
            categories_card.controls.append(
                ft.Container(
                    width=140,
                    height=90,
                    bgcolor=BG,
                    border_radius=15,
                    padding=12,
                    on_click=lambda e, c=cat: select_category(c),
                    content=ft.Column([
                        ft.Text(f"{count} Notes", size=12, color="white"),
                        ft.Text(cat, size=14, color="white"),
                        ft.Container(
                            height=4,
                            bgcolor="white24",
                            border_radius=2,
                            content=ft.Container(
                                bgcolor=PINK, 
                                width=60 if cat == selected_category.current.value else 0
                            )
                        )
                    ])
                )
            )
        page.update()

    def select_category(category):
        selected_category.current.value = category
        filter_notes()
        update_categories()

    def handle_share(note_id):
        try:
            response = api.get_share_url(note_id)
            if response and response.ok:
                share_data = response.json()
                page.dialog = ft.AlertDialog(
                    title=ft.Text("Share Link"),
                    content=ft.Column([
                        ft.Text(share_data['share_url'], selectable=True),
                        ft.ElevatedButton(
                            "Copy Link",
                            on_click=lambda e: page.set_clipboard(share_data['share_url']))
                    ]),
                    on_dismiss=lambda e: page.update()
                )
                page.dialog.open = True
            else:
                show_snackbar(page, "Failed to generate share link")
            page.update()
        except Exception as e:
            show_snackbar(page, f"Sharing failed: {str(e)}")

    def build_note_card(note):
        delete_btn = ft.IconButton(
            icon=ft.icons.DELETE,
            icon_color="red",
            visible=False,
            on_click=lambda e, nid=note.get('id', note.get('local_id')): delete_note(nid)
        )

        share_btn = ft.IconButton(
            icon=ft.icons.SHARE,
            icon_color="white",
            visible=False,
            on_click=lambda e, nid=note.get('id', note.get('local_id')): handle_share(nid)
        )

        checkbox = ft.Checkbox(
            label=note["title"],
            label_style=ft.TextStyle(color="white"),
            value=False,
            check_color=ft.colors.WHITE,
            fill_color=PINK,
            on_change=lambda e: [
                setattr(delete_btn, "visible", e.control.value),
                setattr(share_btn, "visible", e.control.value),
                page.update()
            ]
        )

        tags_row = ft.Row(
            [ft.Text(f"@{user['username']}", color=PINK, size=10) 
             for user in note.get('tagged_users', [])],
            wrap=True,
            spacing=2
        )

        return ft.Container(
            height=80,
            bgcolor=BG,
            border_radius=20,
            padding=15,
            content=ft.Column([
                ft.Row([
                    checkbox,
                    ft.Container(
                        bgcolor=PINK,
                        border_radius=10,
                        padding=ft.padding.symmetric(5, 10),
                        content=ft.Text(
                            note.get("category", "Uncategorized"),
                            size=12,
                            color="white"
                        )
                    ),
                    ft.Row([
                        share_btn,
                        delete_btn
                    ], spacing=5)
                ], alignment="spaceBetween"),
                tags_row,
                ft.Text(
                    note.get("content", "")[:50] + "...", 
                    size=12, 
                    color="white54"
                )
            ]),
            on_click=lambda e, nid=note.get('id', note.get('local_id')), cb=checkbox: (
                page.go(f"/notes?note_id={nid}") if not cb.value else None
            )
        )

    def filter_notes():
        query = search_field.value.strip().lower()
        current_category = selected_category.current.value
        
        filtered_notes = all_notes_data
        
        if current_category != "All":
            if current_category == "Tagged":
                if api.token:
                    current_user_id = (page.client_storage.get("current_user") or {}).get('id')
                    filtered_notes = [
                        n for n in filtered_notes 
                        if current_user_id in [u.get('id') for u in n.get('tagged_users', [])]
                    ]
                else:
                    filtered_notes = []
            else:
                filtered_notes = [n for n in filtered_notes if n.get("category") == current_category]
        
        if query:
            filtered_notes = [
                n for n in filtered_notes
                if (query in n["title"].lower() or 
                    query in n.get("content", "").lower() or 
                    query in n.get("category", "").lower() or
                    any(query in user['username'].lower() for user in n.get('tagged_users', [])))
            ]
        
        tasks.controls.clear()
        for note in filtered_notes:
            tasks.controls.append(build_note_card(note))
        page.update()

    def load_notes():
        nonlocal all_notes_data
        try:
            tasks.controls.clear()
            loading.visible = True
            page.update()

            server_notes = []
            local_notes = page.client_storage.get("local_notes") or []
            
            if api.token:
                response = api.get_notes()
                if response and response.status_code == 200:
                    server_notes = response.json()
                    merged_notes = []
                    local_ids = {n['local_id'] for n in local_notes if 'local_id' in n}
                    
                    # Merge server notes with local notes
                    for note in server_notes + local_notes:
                        if note.get('local_id') not in local_ids:
                            merged_notes.append(note)
                    
                    all_notes_data = merged_notes
            else:
                all_notes_data = [n for n in local_notes if not n.get('synced')]

            update_categories()
            filter_notes()

        except Exception as e:
            show_snackbar(page, f"Error loading notes: {str(e)}")
        finally:
            loading.visible = False
            page.update()

    def open_search():
        search_icon.visible = False
        search_field.visible = True
        close_search_btn.visible = True
        page.update()

    def close_search():
        search_field.visible = False
        close_search_btn.visible = False
        search_icon.visible = True
        search_field.value = ""
        filter_notes()
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
                [{
                    "title": n["title"],
                    "content": n["content"],
                    "category": n.get("category", "Uncategorized"),
                    "local_id": n.get("local_id"),
                    "tagged_emails": n.get("tagged_emails", [])
                } for n in local_notes]
            )
            
            if response and response.status_code == 200:
                page.client_storage.remove("local_notes")
                data = response.json()
                page.client_storage.set("auth_token", data.get('token', ''))
                page.client_storage.set("current_user", data.get('user', {}))
                
                nonlocal user_name
                user_data = data.get('user', {})
                user_name = user_data.get("username", "Guest")
                sidebar_username.current.value = user_name
                welcome_text.current.value = f"Welcome back, {user_name}!"
                
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

    # Refs for dynamic updates
    sidebar_username = ft.Ref[ft.Text]()
    welcome_text = ft.Ref[ft.Text]()

    sidebar = ft.Container(
        width=280,
        height=page.height,
        bgcolor=BG,
        padding=20,
        content=ft.Column(
            [
                ft.IconButton(ft.icons.ARROW_BACK, on_click=toggle_sidebar),
                ft.Text(user_name, ref=sidebar_username, size=18, weight="bold", color="white"),
                ft.Divider(height=20, color="white24"),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.SYNC, color="black"),
                    title=ft.Text("Sync Now", color="white"),
                    on_click=sync_notes
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.SETTINGS, color="black"),
                    title=ft.Text("Settings", color="white")
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.icons.EXIT_TO_APP, color="red"),
                    title=ft.Text("Logout", color="white"),
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
                            search_icon,
                            search_field,
                            close_search_btn,
                            ft.IconButton(ft.icons.NOTIFICATIONS_NONE)
                        ], spacing=5)
                    ],
                    alignment="spaceBetween"
                ),
                ft.Text(f"Welcome back, {user_name}!", ref=welcome_text, 
                       size=20, weight="bold"),
                ft.Text("CATEGORIES", size=12, color=BG),
                ft.Container(height=100, content=categories_card),
                ft.Text("YOUR NOTES", size=12, color=BG),
                ft.Container(
                    expand=True,
                    content=ft.Column([
                        ft.ListView(
                            controls=[ft.Container(expand=True, content=tasks)],
                            expand=True
                        )
                    ], spacing=20)
                ),
            ],
            expand=True
        ) 
    )
    
    fab = ft.FloatingActionButton(
        icon=ft.icons.ADD,
        on_click=lambda e: page.go("/notes"),
        bgcolor=PINK,
        right=20,
        bottom=20,
        shape=ft.CircleBorder(),
    )
    
    load_notes()
    refresh_notes.append(load_notes)
    return ft.View(
        "/",
        [
            ft.Stack(
                [
                    main_content,
                    fab,
                    sidebar
                ],
                expand=True
            ),
            loading
        ]
    )
 
# #                 ft.Text("CATEGORIES", size=12, color=BG),
# #                 ft.Container(height=100, content=categories_card),
# #                 ft.Text("YOUR NOTES", size=12, color=BG),
# #                 ft.Container(
# #                     expand=True,
# #                     content=ft.Column([
# #                         ft.ListView(
# #                             controls=[ft.Container(expand=True, content=tasks)],
# #                             expand=True
# #                         )
# #                     ], spacing=20)
# #                 ),
# #             ],
# #             expand=True
# #         ) 
# #     )
    
# #     fab = ft.FloatingActionButton(
# #         icon=ft.icons.ADD,
# #         on_click=lambda e: page.go("/notes"),
# #         bgcolor=PINK,
# #         right=20,
# #         bottom=20,
# #         shape=ft.CircleBorder(),
# #     )
    
# #     load_notes()
# #     refresh_notes.append(load_notes)
# #     return ft.View(
# #         "/",
# #         [
# #             ft.Stack(
# #                 [
# #                     main_content,
# #                     fab,
# #                     sidebar
# #                 ],
# #                 expand=True
# #             ),
# #             loading
# #         ]
# #     )


# import flet as ft
# from api import api
# from utilities import show_snackbar

# def main_notes_view(page: ft.Page, refresh_notes):
#     BG = "#041955"
#     PINK = ft.colors.PINK_ACCENT
#     user_name = (page.client_storage.get("current_user") or {}).get("username", "Guest")
#     tasks = ft.ListView(expand=True, spacing=10)
#     loading = ft.ProgressBar(visible=False)
#     show_sidebar = False
#     all_notes_data = []
#     categories = ["All", "Business", "Family", "Friends", "Personal", "Tagged"]
#     selected_category = ft.Ref[ft.Text]()
#     selected_category.current = ft.Text("All")

#     # UI Elements
#     search_field = ft.TextField(
#         hint_text="Search notes...",
#         on_change=lambda e: filter_notes(),
#         visible=False,
#         expand=True,
#         height=40,
#         text_size=14,
#         border_color="transparent",
#         content_padding=5,
#     )

#     close_search_btn = ft.IconButton(
#         ft.icons.CLOSE,
#         on_click=lambda e: close_search(),
#         visible=False,
#     )

#     search_icon = ft.IconButton(
#         ft.icons.SEARCH,
#         on_click=lambda e: open_search(),
#     )

#     # Category Cards
#     categories_card = ft.ListView(
#         horizontal=True,
#         spacing=10,
#         height=100,
#     )

#     def update_categories():
#         categories_card.controls.clear()
#         for cat in categories:
#             count = len([n for n in all_notes_data if 
#                 (n.get("category") )== cat or 
#                 (cat == "All" and n) or
#                 (cat == "Tagged" and any(u['id'] == page.client_storage.get("current_user", {}).get('id') )
#                 for u in n.get('tagged_users', []))])
#             categories_card.controls.append(
#                 ft.Container(
#                     width=140,
#                     height=90,
#                     bgcolor=BG,
#                     border_radius=15,
#                     padding=12,
#                     on_click=lambda e, c=cat: select_category(c),
#                     content=ft.Column([
#                         ft.Text(f"{count} Notes", size=12, color="white"),
#                         ft.Text(cat, size=14, color="white"),
#                         ft.Container(
#                             height=4,
#                             bgcolor="white24",
#                             border_radius=2,
#                             content=ft.Container(
#                                 bgcolor=PINK, 
#                                 width=60 if cat == selected_category.current.value else 0
#                             )
#                         )
#                     ])
#                 )
#             )
#         page.update()

#     def select_category(category):
#         selected_category.current.value = category
#         filter_notes()
#         update_categories()

#     def handle_share(note_id):
#         try:
#             response = api.get_share_url(note_id)
#             if response and response.ok:
#                 share_data = response.json()
#                 page.dialog = ft.AlertDialog(
#                     title=ft.Text("Share Link"),
#                     content=ft.Column([
#                         ft.Text(share_data['share_url'], selectable=True),
#                         ft.ElevatedButton(
#                             "Copy Link",
#                             on_click=lambda e: page.set_clipboard(share_data['share_url']))
#                     ]),
#      