import flet as ft
from api import api
from views.main_notes import main_notes_view
from utilities import show_snackbar


def login_app(page: ft.Page):
    # Change username field to email field
    email_field = ft.TextField(label="Email", autofocus=True)
    password_field = ft.TextField(label="Password", password=True)
    error_text = ft.Text(color="red")
    loading = ft.ProgressBar(visible=False)

    def handle_login(e):
        error_text.value = ""
        email = email_field.value.strip()  # Changed from username to email
        password = password_field.value

        if not all([email, password]):
            error_text.value = "All fields are required"
            return page.update()

        try:
            loading.visible = True
            page.update()
            
            # Update to use email instead of username
            response = api.login(email, password)
            
            if response and response.status_code == 200:
                data = response.json()
                # Set credentials in both API and client storage
                api.set_credentials(token=data['token'])
                page.client_storage.set("auth_token", data['token'])
                page.client_storage.set("current_user", data['user'])
                page.data["current_user"] = data['user']
                page.views.clear()
                page.route = "/"
                page.views.append(main_notes_view(page, []))
                page.update()
                
            else:
                handle_error(response)

        except Exception as e:
            error_text.value = f"Error: {str(e)}"
        finally:
            loading.visible = False
            page.update()

    def handle_error(response):
        try:
            if not response:
                error_text.value = "Cannot connect to server"
                return
                
            error_data = response.json()
            # Handle different error formats
            if 'non_field_errors' in error_data:
                error_text.value = "\n".join(error_data['non_field_errors'])
            elif 'detail' in error_data:
                error_text.value = error_data['detail']
            else:
                error_text.value = "Invalid email or password"
                
        except:
            error_text.value = f"Login failed (status {response.status_code})"

    return ft.View(
        "/login",
        [
            ft.Column(
                [
                    ft.Text("Login", size=24, weight="bold"),
                    email_field,  # Changed from username_field
                    password_field,
                    ft.ElevatedButton("Login", on_click=handle_login),
                    ft.TextButton("Create Account", on_click=lambda e: page.go("/signup")),
                    loading,
                    error_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            )
        ]
    )