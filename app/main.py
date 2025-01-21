import os
from fastapi import FastAPI, File, Header, Body, Response, UploadFile
from fastapi.responses import JSONResponse
from firebase_admin import auth, initialize_app
from typing import Annotated

import api.categories
import api.transactions
from dependencies.authentication_handler import get_user_data_from_token, get_uid_from_token

from google.cloud import storage

bucket_name = 'ex-bucket-x'

firebase_app = initialize_app()

app = FastAPI()
app.include_router(api.transactions.router)
app.include_router(api.categories.router)

@app.get("/")
async def root():
    port = os.getenv("PORT", "Not Set")
    return {"message": f"Hello World, PORT: {port}"}

@app.get('/user')
async def get_user(Authorization: Annotated[str | None, Header()] = None):
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
async def get_image():
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
async def download(blob_name: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    contents = blob.download_as_bytes()

    return Response(content=contents, media_type="image/png")

@app.post('/upload/{file_name}')
async def upload(file_name: str, file: Annotated[bytes, File()]):
    f = open(f'/gcs-1/{file_name}', 'a')
    f.write(file)
    f.close()
    return {
        'message': 'success'
    }

    # try:
    #     return open('/gcs-1/Flag_of_the_United_States.png', 'r')
    # except Exception as error:
    #     return JSONResponse(content="error : " + error.__str__(), status_code=500)