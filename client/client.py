# client.py
import requests
import os
from dotenv import load_dotenv
import sys

load_dotenv()

def get_headers(client_id):
    key_var = f"API_KEY_{client_id}"
    api_key = os.environ.get(key_var)
    if not api_key:
        raise ValueError(f"Missing API key for {client_id}")
    return {
        "X-Client-Id": client_id,  # lowercase 'Id'
        "X-Api-Key": api_key       # lowercase 'Api' and 'Key'
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
    return response
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
    return response
def list_files(client_id: str):
    url = "https://127.0.0.1:8443/list"
    headers = get_headers(client_id)
    response = requests.get(url, headers=headers, verify=False)
    print("Request URL:", url)
    print("Request headers:", headers)
    print("Response status:", response.status_code)
    print("Response body:", response.text)

    print("Files:", response.json())

    return response

# Example usage:
# upload_file("testfile.txt", "client123")
# download_file("testfile.txt", "client123")
# list_files("client123")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python client.py <command> <client_id> [filename]")
        print("Commands: list, upload, download")
        sys.exit(1)

    command = sys.argv[1]
    client_id = sys.argv[2]

    if command == "list":
        list_files(client_id)
    elif command == "upload":
        if len(sys.argv) < 4:
            print("Usage: python client.py upload <client_id> <file_path>")
            sys.exit(1)
        file_path = sys.argv[3]
        upload_file(file_path, client_id)
    elif command == "download":
        if len(sys.argv) < 4:
            print("Usage: python client.py download <client_id> <filename>")
            sys.exit(1)
        filename = sys.argv[3]
        download_file(filename, client_id)
    else:
        print(f"Unknown command: {command}")
