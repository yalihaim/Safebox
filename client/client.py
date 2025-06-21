# client.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_headers(client_id):
    key_var = f"API_KEY_{client_id}"
    api_key = os.environ.get(key_var)
    if not api_key:
        raise ValueError(f"Missing API key for {client_id}")
    return {
        "X-Client-ID": client_id,
        "X-API-Key": api_key
    }

def upload_file(file_path: str, client_id: str):
    url = "https://localhost:8443/upload"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        headers = get_headers(client_id)
        response = requests.post(url, files=files, headers=headers, verify=False)
        print("Upload Response:", response.status_code, response.text)
    if response.status_code == 200:
        os.remove(file_path)
        print("Local file deleted.")

def download_file(filename: str, client_id: str):
    url = f"https://localhost:8443/download?name={filename}"
    headers = get_headers(client_id)
    response = requests.get(url, headers=headers, verify=False)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            f.write(response.content)
        print("Download complete.")
    else:
        print("Download failed:", response.status_code, response.text)

def list_files(client_id: str):
    url = "https://localhost:8443/list"
    headers = get_headers(client_id)
    response = requests.get(url, headers=headers, verify=False)
    print("Files:", response.json())

# Example usage:
# upload_file("testfile.txt", "client123")
# download_file("testfile.txt", "client123")
# list_files("client123")
