import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class DriveFetcher:
    def __init__(self, folder_id):
        self.folder_id = folder_id
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(f"{SERVICE_ACCOUNT_FILE} not found. Please add it to the root directory.")
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = build('drive', 'v3', credentials=creds)

    def list_files(self):
        print(f"--- Fetching files from Drive Folder ID: {self.folder_id} ---")
        query = f"'{self.folder_id}' in parents and mimeType='text/plain'"
        results = self.service.files().list(
            q=query,
            fields="nextPageToken, files(id, name)"
        ).execute()
        files = results.get('files', [])
        print(f"... Found {len(files)} files.")
        return files

    def download_file(self, file_id, file_name):
        print(f"... Downloading '{file_name}' (ID: {file_id})")
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        print(f"... Download complete.")
        return fh.getvalue().decode('utf-8')