import os
from fastapi import FastAPI, Header, Body
from fastapi.responses import JSONResponse
from firebase_admin import auth, firestore, initialize_app
from typing import Annotated
from google.cloud.firestore_v1 import aggregation

from model.transaction.transaction_request_body import TransactionRequestBody

firebase_app = initialize_app()
db = firestore.client()

app = FastAPI()

def get_uid_from_token(bearer_token: str):
    token = bearer_token.replace('Bearer ','')
    decoded_token = auth.verify_id_token(id_token = token)
    return decoded_token['uid']

def get_user_data_from_token(bearer_token: str):
    uid = get_uid_from_token(bearer_token)
    return auth.get_user(uid)

@app.get("/")
async def root():
    port = os.getenv("PORT", "Not Set")
    return {"message": f"Hello World, PORT: {port}"}

@app.get("/test")
async def test(Authorization: Annotated[str | None, Header()] = None):
    user = get_user_data_from_token(bearer_token=Authorization)
    return user._data["email"]

@app.get('/user')
async def get_user(Authorization: Annotated[str | None, Header()] = None):
    return get_user_data_from_token(bearer_token=Authorization)

@app.post("/transaction")
async def add_transaction(
        request_body: Annotated[TransactionRequestBody, Body()],
        Authorization: Annotated[str | None, Header()] = None
    ):
    try:
        user = get_user_data_from_token(bearer_token=Authorization)
    except Exception as error:
        return JSONResponse(content="error : " + error.__str__(), status_code=401)
    email = str(user._data["email"])

    db.collection("transactions").document(user.uid).set(
            {
                "email": email
            }
        )
        
    doc_ref = db.collection("transactions/{}/data".format(str(user.uid))).document()

    request_body.set_id(doc_ref.id)
    doc_ref.set(request_body.to_dict())
    
    return {
        'transaction': request_body.to_dict(),
        'message': 'success'
    }

@app.get("/transaction")
async def get_transaction(Authorization: Annotated[str | None, Header()] = None):
    try:
        uid = get_uid_from_token(bearer_token=Authorization)
    except Exception as error:
        return JSONResponse(content="error : " + error.__str__(), status_code=401)
    
    data = []
    for item in db.collection("transactions/{}/data".format(str(uid))).get():
        data.append(item.to_dict())
    return {
        "transactions": data,
        'message': 'success'
    }

@app.put("/transaction")
async def update_transaction(
        request_body: TransactionRequestBody,
        Authorization: Annotated[str | None, Header()] = None
    ):
    try:
        uid = get_uid_from_token(bearer_token=Authorization)
    except Exception as error:
        return JSONResponse(content="error : " + error.__str__(), status_code=401)
    
    doc_ref = db.collection("transactions/{}/data".format(str(uid))).document(request_body.id)
    doc_ref.update(request_body.to_dict())
    
    return {
            "transaction": request_body.to_dict(),
            "message":"success"
        }

@app.delete('/transaction')
async def delete_transaction(
    transaction_id: str,
    Authorization: Annotated[str | None, Header()] = None
):
    try:
        uid = get_uid_from_token(bearer_token=Authorization)
    except Exception as error:
        return JSONResponse(content="error : " + error.__str__(), status_code=401)
    
    doc_ref = db.collection("transactions/{}/data".format(str(uid))).document(transaction_id)
    doc_ref.delete()

    return 'success'