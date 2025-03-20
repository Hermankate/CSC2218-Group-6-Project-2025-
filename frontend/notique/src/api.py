import uuid
import requests

class API:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.local_id = None
        
    def set_credentials(self, token=None, local_id=None):
        self.token = token
        self.local_id = local_id or str(uuid.uuid4())  # Generate local ID if not provided
        
    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            # Changed from Bearer to Token for Django REST Framework
            headers["Authorization"] = f"Token {self.token}"
        if self.local_id and not self.token:
            headers["X-Local-ID"] = self.local_id
        return headers
        
    def register(self, username, email, password):
        try:
            response = requests.post(
                f"{self.base_url}/api/register/",
                json={"username": username, "email": email, "password": password}
            )
            if response.status_code == 201:
                data = response.json()
                self.set_credentials(token=data.get('token'))
            return response
        except requests.exceptions.ConnectionError:
            return None
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return None
        
    def login(self, email, password):  # Changed from username to email
        try:
            response = requests.post(
                f"{self.base_url}/api/login/",
                json={"username": email, "password": password}  # Changed to email
            )
            if response.status_code == 200:
                data = response.json()
                self.set_credentials(token=data.get('token'))
            return response
        except requests.exceptions.ConnectionError:
            return None
        except Exception as e:
            print(f"Login error: {str(e)}")
            return None
            
    def get_notes(self):
        try:
            response = requests.get(
                f"{self.base_url}/api/notes/", 
                headers=self._headers()
            )
            if response.status_code == 401:
                self.handle_unauthorized()
            return response
        except requests.exceptions.ConnectionError:
            return None
            
    def create_note(self, title, content):
        try:
            return requests.post(
                f"{self.base_url}/api/notes/",
                headers=self._headers(),
                json={
                    "title": title, 
                    "content": content,
                    "local_id": self.local_id  # Include local ID for sync
                }
            )
        except requests.exceptions.ConnectionError:
            return None

    def update_note(self, note_id, title, content):
        try:
            return requests.put(
                f"{self.base_url}/api/notes/{note_id}/",
                headers=self._headers(),
                json={"title": title, "content": content}
            )
        except requests.exceptions.ConnectionError:
            return None

    def delete_note(self, note_id):
        try:
            return requests.delete(
                f"{self.base_url}/api/notes/{note_id}/",
                headers=self._headers()
            )
        except requests.exceptions.ConnectionError:
            return None

    def sync_notes(self, local_id, notes):
        try:
            return requests.post(
                f"{self.base_url}/api/sync/",
                json={"local_storage_id": local_id, "notes": notes}
            )
        except requests.exceptions.ConnectionError:
            return None




api = API("http://127.0.0.1:8000")
