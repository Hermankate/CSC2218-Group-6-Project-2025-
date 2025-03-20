import uuid
import flet as ft
from src.api import api

def welcome_view(page: ft.Page):
    def handle_skip(e):
        local_id = str(uuid.uuid4())
        page.client_storage.set("local_storage_id", local_id)
        api.set_credentials(local_id=local_id)
        page.go("/")

    return ft.View(
        "/welcome",
        [
            ft.Column(
                [
                    ft.Text("Welcome to Notique", size=24, weight="bold"),
                    ft.Row([
                        ft.ElevatedButton("Sign Up", on_click=lambda e: page.go("/signup")),
                        ft.ElevatedButton("Continue Offline", on_click=handle_skip),
                    ], alignment=ft.MainAxisAlignment.CENTER)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            )
        ]
    )