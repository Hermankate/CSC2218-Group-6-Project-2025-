import flet as ft
from src.api import api
from src.utilities import show_snackbar

def signup_app(page: ft.Page):
    username_field = ft.TextField(label="Username", autofocus=True)
    email_field = ft.TextField(label="Email")
    password_field = ft.TextField(label="Password", password=True, can_reveal_password=True)
    error_text = ft.Text(color="red")
    loading = ft.ProgressBar(visible=False)

    def handle_submit(e):
        error_text.value = ""
        username = username_field.value.strip()
        email = email_field.value.strip()
        password = password_field.value

        if not all([username, email, password]):
            error_text.value = "All fields are required"
            page.update()
            return

        try:
            loading.visible = True
            page.update()
            
            response = api.register(username, email, password)
            
            if response is None:
                error_text.value = "Cannot connect to server"
                return
                
            print(f"Response Status: {response.status_code}")
            print(f"Response Content: {response.text}")

            if response.status_code == 201:
                data = response.json()
                api.set_credentials(token=data['token'])
                page.client_storage.set("auth_token", data['token'])
                page.client_storage.set("current_user", data['user'])
                page.data["current_user"] = data['user']
                page.go("/")
            else:
                try:
                    error_data = response.json()
                    error_text.value = "\n".join(
                        [f"{k}: {v}" for k, v in error_data.items()]
                    ) if isinstance(error_data, dict) else str(error_data)
                except:
                    error_text.value = f"Server error: {response.status_code}"

        except Exception as e:
            error_text.value = f"Error: {str(e)}"
        finally:
            loading.visible = False
            page.update()

    return ft.View(
        "/signup",
        [
            ft.Column(
                [
                    ft.Text("Create Account", size=24, weight="bold"),
                    username_field,
                    email_field,
                    password_field,
                    ft.ElevatedButton("Sign Up", on_click=handle_submit),
                    ft.TextButton("Have an account? Login", 
                               on_click=lambda e: page.go("/login")),
                    loading,
                    error_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        ]
    )