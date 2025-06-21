# server.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Header
from fastapi.responses import FileResponse
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import secrets
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

BASE_DIR = Path("./secure_store")
BASE_DIR.mkdir(exist_ok=True)

# Load encryption key
key_hex = os.environ.get("FILE_ENCRYPTION_KEY")
if not key_hex:
    raise RuntimeError("Missing FILE_ENCRYPTION_KEY environment variable")
SECRET_KEY = bytes.fromhex(key_hex)

# Load client tokens from .env
raw_tokens = os.environ.get("CLIENT_TOKENS", "")
CLIENT_TOKENS = dict(token.split(":") for token in raw_tokens.split(",") if ":" in token)

def encrypt_file(data: bytes, key: bytes) -> bytes:
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    encrypted = aesgcm.encrypt(nonce, data, None)
    return nonce + encrypted

def decrypt_file(encrypted: bytes, key: bytes) -> bytes:
    nonce = encrypted[:12]
    ciphertext = encrypted[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)

def validate_client(client_id: str, api_key: str):
    expected_token = CLIENT_TOKENS.get(client_id)
    if not expected_token or api_key != expected_token:
        raise HTTPException(status_code=403, detail="Invalid API token or client ID")

@app.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    x_client_id: str = Header(...),
    x_api_key: str = Header(...)
):
    validate_client(x_client_id, x_api_key)
    client_dir = BASE_DIR / x_client_id
    client_dir.mkdir(parents=True, exist_ok=True)
    destination = client_dir / file.filename
    file_data = await file.read()
    encrypted_data = encrypt_file(file_data, SECRET_KEY)
    with open(destination, "wb") as f:
        f.write(encrypted_data)
    return {"message": "Upload successful"}

@app.get("/download")
def download_file(
    request: Request,
    name: str,
    x_client_id: str = Header(...),
    x_api_key: str = Header(...)
):
    validate_client(x_client_id, x_api_key)
    filepath = BASE_DIR / x_client_id / name
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    with open(filepath, "rb") as f:
        encrypted_data = f.read()
    try:
        decrypted_data = decrypt_file(encrypted_data, SECRET_KEY)
    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")
    temp_file = filepath.parent / f".tmp_{name}"
    with open(temp_file, "wb") as f:
        f.write(decrypted_data)
    return FileResponse(temp_file, filename=name)

@app.get("/list")
def list_files(
    request: Request,
    x_client_id: str = Header(...),
    x_api_key: str = Header(...)
):
    print("📥 Received GET /list request from:", x_client_id, flush=True)
    validate_client(x_client_id, x_api_key)
    client_dir = BASE_DIR / x_client_id
    if not client_dir.exists():
        return {"files": []}
    return {"files": os.listdir(client_dir)}

