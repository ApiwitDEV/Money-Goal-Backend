import os
from fastapi import FastAPI, File, Header, Body, Response, UploadFile
from fastapi.responses import JSONResponse
from firebase_admin import auth, initialize_app
from typing import Annotated

import api.categories
import api.receipt
import api.transactions
from dependencies.authentication_handler import get_user_data_from_token, get_uid_from_token

import vertexai
from vertexai.generative_models import GenerativeModel

from google.cloud import storage

bucket_name = 'ex-bucket-x'

PROJECT_ID = 'money-goal-bfc71'

firebase_app = initialize_app()

import vertexai
from vertexai.generative_models import GenerativeModel

vertexai.init(project=PROJECT_ID, location="us-central1")

app = FastAPI()
app.include_router(api.transactions.router)
app.include_router(api.categories.router)
app.include_router(api.receipt.router)

@app.get("/")
def root():
    port = os.getenv("PORT", "Not Set")
    return {"message": f"Hello World, PORT: {port}"}

@app.get('/user')
def get_user(Authorization: Annotated[str | None, Header()] = None):
    return get_user_data_from_token(Authorization)

@app.get('/revoke-token')
def revoke_token(Authorization: Annotated[str | None, Header()] = None):
    try:
        uid = get_uid_from_token(Authorization)
    except Exception as error:
        return JSONResponse(content="error : " + error.__str__(), status_code=401)
    
    # Revoke tokens on the backend.
    auth.revoke_refresh_tokens(uid)
    user = auth.get_user(uid)
    # Convert to seconds as the auth_time in the token claims is in seconds.
    revocation_second = user.tokens_valid_after_timestamp / 1000
    return 'Tokens revoked at: {0}'.format(revocation_second)

@app.get('/image')
def get_image():
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name)
    list = []
    for i in blobs:
        list.append(i.name)
    return {
        'image_list': list,
        'message': 'success'
    }

@app.get('/download/{blob_name}')
def download(blob_name: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    contents = blob.download_as_bytes()

    return Response(content=contents, media_type="image/png")

@app.post('/upload/{file_name}')
def upload(uploaded_file: UploadFile | None = None):
    destination_blob_name = uploaded_file.filename
    storage_client = storage.Client()
    # content = await file.read()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(uploaded_file.file)
    uploaded = blob.download_as_bytes()

    return Response(content=uploaded, media_type="image/png")

@app.post('/try-ai')
def try_ai(prompt: str = ""):
    model = GenerativeModel("gemini-1.5-flash-002")
    response = model.generate_content(prompt)

    return { 'prompt': prompt, 'result': response.to_dict() }