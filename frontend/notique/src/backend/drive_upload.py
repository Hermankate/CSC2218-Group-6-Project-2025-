from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

def upload_to_drive(file_path):
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)

    file = drive.CreateFile({'title': file_path})
    file.SetContentFile(file_path)
    file.Upload()
    print("Uploaded successfully!")
