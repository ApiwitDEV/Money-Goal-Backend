import os
from fastapi import FastAPI, Header
from firebase_admin import auth
from typing import Annotated

app = FastAPI()

def get_uid_from_token(bearer_token):
    try:
        token = bearer_token.replace('Bearer ','')
        uid = auth.verify_id_token(id_token=token)
    except:
        uid = "An exception occurred"
    return token, uid

@app.get("/")
async def root():
    port = os.getenv("PORT", "Not Set")
    return {"message": f"Hello World, PORT: {port}"}

@app.get("/test")
async def test(Authorization: Annotated[str | None, Header()] = None):
    token, uid = get_uid_from_token(bearer_token=Authorization)
    
    return {"bearer token": token, "uid": uid}

@app.post("/post-x")
async def post():
    return {}