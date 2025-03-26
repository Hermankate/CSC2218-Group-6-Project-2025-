import uuid
import requests

class API:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.local_id = None

    def get_note(self, note_id):
        try:
            return requests.get(
                f"{self.base_url}/api/notes/{note_id}/",
                headers=self._headers()
            )
        except requests.exceptions.ConnectionError:
            return None

    def set_credentials(self, token=None, local_id=None):
        self.token = token
        self.local_id = local_id or str(uuid.uuid4())
        
    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
        if self.local_id and not self.token:
            headers["X-Local-ID"] = self.local_id
        return headers

    def _handle_response(self, response):
        if response.status_code not in (200, 201):
            print(f"API Error: {response.status_code} - {response.text}")
        return response

    def register(self, username, email, password):
        try:
            response = requests.post(
                f"{self.base_url}/api/register/",
                json={
                    "username": username,  # Include username (optional)
                    "email": email,
                    "password": password
                }
            )
            if response.status_code == 201:
                data = response.json()
                self.set_credentials(token=data.get('token'))
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {str(e)}")
            return None
    def login(self, email, password):
        try:
            response = requests.post(
                f"{self.base_url}/api/login/",
                json={"email": email, "password": password}
            )
            if response.status_code == 200:
                data = response.json()
                self.set_credentials(token=data.get('token'))
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {str(e)}")
            return None

    def get_notes(self):
        try:
            response = requests.get(
                f"{self.base_url}/api/notes/", 
                headers=self._headers()
            )
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {str(e)}")
            return None

    def create_note(self, data):
        try:
            response = requests.post(
                f"{self.base_url}/api/notes/",
                headers=self._headers(),
                json={
                    "title": data['title'], 
                    "content": data['content'],
                    "category": data.get('category', 'Uncategorized'),
                    "local_id": self.local_id
                }
            )
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {str(e)}")
            return None

    def update_note(self, note_id, data):
        try:
            response = requests.put(
                f"{self.base_url}/api/notes/{note_id}/",
                headers=self._headers(),
                json={
                    "title": data['title'],
                    "content": data['content'],
                    "category": data.get('category', 'Uncategorized')
                }
            )
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {str(e)}")
            return None

    def delete_note(self, note_id):
        try:
            response = requests.delete(
                f"{self.base_url}/api/notes/{note_id}/",
                headers=self._headers()
            )
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {str(e)}")
            return None

    def sync_notes(self, local_id, notes):
        try:
            response = requests.post(
                f"{self.base_url}/api/sync/",
                json={
                    "local_storage_id": local_id,
                    "notes": [{
                        "title": n["title"],
                        "content": n["content"],
                        "category": n.get("category", "Uncategorized"),
                        "local_id": n.get("local_id")
                    } for n in notes]
                }
            )
            return self._handle_response(response)
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {str(e)}")
            return None

# Usage
api = API("http://hermankatende.pythonanywhere.com")
#api = API("http://127.0.0.1:8000")

# api=API("https://group6webapi.pythonanywhere.com")\