import os
from fastapi import FastAPI, Header, Body
from fastapi.responses import JSONResponse
from firebase_admin import auth, firestore, initialize_app
from typing import Annotated

from model.category.category_request_body import CategoryRequestBody
from model.transaction.transaction_request_body import TransactionRequestBody

firebase_app = initialize_app()
db = firestore.client()

app = FastAPI()

def get_uid_from_token(bearer_token: str):
    token = bearer_token.replace('Bearer ','')
    decoded_token = auth.verify_id_token(id_token = token, check_revoked=True)
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

@app.post("/transactions")
async def add_transaction(
        request_body: Annotated[TransactionRequestBody, Body()],
        Authorization: Annotated[str | None, Header()] = None
    ):
    try:
        user = get_user_data_from_token(bearer_token=Authorization)
    except auth.RevokedIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 1
                },
            status_code=401
        )
    except auth.UserDisabledError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 2
                },
            status_code=401
        )
    except auth.InvalidIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 3
                },
            status_code=401
        )
    except Exception as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 4
                },
            status_code=401
        )
    
    email = str(user._data["email"])

    db.collection("Transactions").document(user.uid).set(
            {
                "email": email
            }
        )
        
    doc_ref = db.collection("Transactions/{}/data".format(str(user.uid))).document()

    request_body.set_id(doc_ref.id)
    request_body.set_create_time()
    request_body.set_update_time()
    doc_ref.set(request_body.to_dict())
    
    return {
        'transaction': request_body.to_dict(),
        'message': 'success'
    }

@app.get("/transactions")
async def get_transaction(Authorization: Annotated[str | None, Header()] = None):
    try:
        user = get_user_data_from_token(bearer_token=Authorization)
    except auth.RevokedIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 1
                },
            status_code=401
        )
    except auth.UserDisabledError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 2
                },
            status_code=401
        )
    except auth.InvalidIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 3
                },
            status_code=401
        )
    except Exception as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 4
                },
            status_code=401
        )
    
    data = []
    for item in db.collection("Transactions/{}/data".format(str(user.uid))).get():
        data.append(item.to_dict())
    return {
        "transactions": data,
        'message': 'success'
    }

@app.put("/transactions")
async def update_transaction(
        request_body: TransactionRequestBody,
        Authorization: Annotated[str | None, Header()] = None
    ):
    try:
        user = get_user_data_from_token(bearer_token=Authorization)
    except auth.RevokedIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 1
                },
            status_code=401
        )
    except auth.UserDisabledError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 2
                },
            status_code=401
        )
    except auth.InvalidIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 3
                },
            status_code=401
        )
    except Exception as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 4
                },
            status_code=401
        )
    
    doc_ref = db.collection("Transactions/{}/data".format(str(user.uid))).document(request_body.id)
    request_body.set_update_time()
    doc_ref.update(request_body.to_dict())
    
    return {
            "transaction": doc_ref.get().to_dict(),
            "message":"success"
        }

@app.delete('/transactions')
async def delete_transaction(
    ids: Annotated[list, Body()],
    Authorization: Annotated[str | None, Header()] = None
):
    try:
        user = get_user_data_from_token(bearer_token=Authorization)
    except auth.RevokedIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 1
                },
            status_code=401
        )
    except auth.UserDisabledError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 2
                },
            status_code=401
        )
    except auth.InvalidIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 3
                },
            status_code=401
        )
    except Exception as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 4
                },
            status_code=401
        )
    
    for transaction_id in ids:
        doc_ref = db.collection("Transactions/{}/data".format(str(user.uid))).document(transaction_id)
        doc_ref.delete()

    return 'success'

@app.post('/categories')
def add_category(
        category: CategoryRequestBody,
        Authorization: Annotated[str | None, Header()] = None
    ):
    try:
        user = get_user_data_from_token(bearer_token=Authorization)
    except auth.RevokedIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 1
                },
            status_code=401
        )
    except auth.UserDisabledError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 2
                },
            status_code=401
        )
    except auth.InvalidIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 3
                },
            status_code=401
        )
    except Exception as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 4
                },
            status_code=401
        )
    
    email = str(user._data["email"])

    db.collection("Categories").document(user.uid).set(
            {
                "email": email
            }
        )
    
    doc_ref = db.collection('Categories/{}/data'.format(str(user.uid))).document()

    category.set_create_time()
    category.set_update_time()
    doc_ref.set(category.to_dict())

    return {
        'category': category.to_dict(),
        'message': 'success'
    }

@app.get('/categories')
def get_categories(
    Authorization: Annotated[str | None, Header()] = None
):
    try:
        user = get_user_data_from_token(bearer_token=Authorization)
    except auth.RevokedIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 1
                },
            status_code=401
        )
    except auth.UserDisabledError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 2
                },
            status_code=401
        )
    except auth.InvalidIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 3
                },
            status_code=401
        )
    except Exception as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 4
                },
            status_code=401
        )
    
    docs = db.collection('Categories/{}/data'.format(str(user.uid))).get()
    default_categories = db.collection('Categories/Default/data').get()

    categories = []
    for doc in default_categories:
        item = doc.to_dict()
        item.update({'id': doc.id})
        categories.append(item)
    for doc in docs:
        item = doc.to_dict()
        item.update({'id': doc.id})
        categories.append(item)

    return {
        'categories': categories,
        'message': 'success'
    }

@app.put('/categories')
def update_category(
    request_body: CategoryRequestBody,
    Authorization: Annotated[str | None, Header()] = None
):
    try:
        user = get_user_data_from_token(bearer_token=Authorization)
    except auth.RevokedIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 1
                },
            status_code=401
        )
    except auth.UserDisabledError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 2
                },
            status_code=401
        )
    except auth.InvalidIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 3
                },
            status_code=401
        )
    except Exception as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 4
                },
            status_code=401
        )
    
    doc_ref = db.collection("Categories/{}/data".format(str(user.uid))).document(request_body.id)
    request_body.set_update_time()
    doc_ref.update(request_body.to_dict())

    return {
        'category': doc_ref.get().to_dict(),
        'message': 'success'
    }

@app.delete('/categories')
def delete_category(
    ids: Annotated[list, Body()],
    Authorization: Annotated[str | None, Header()] = None
):
    try:
        user = get_user_data_from_token(bearer_token=Authorization)
    except auth.RevokedIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 1
                },
            status_code=401
        )
    except auth.UserDisabledError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 2
                },
            status_code=401
        )
    except auth.InvalidIdTokenError as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 3
                },
            status_code=401
        )
    except Exception as error:
        return JSONResponse(
            content={
                'error_message': error.__str__(),
                'error_code': 4
                },
            status_code=401
        )
    
    for category_id in ids:
        doc_ref = db.collection("Categories/{}/data".format(str(user.uid))).document(str(category_id))
        doc_ref.delete()

    return 'success'

@app.get('/revoke-token')
def revoke_token(Authorization: Annotated[str | None, Header()] = None):
    try:
        uid = get_uid_from_token(bearer_token=Authorization)
    except Exception as error:
        return JSONResponse(content="error : " + error.__str__(), status_code=401)
    
    # Revoke tokens on the backend.
    auth.revoke_refresh_tokens(uid)
    user = auth.get_user(uid)
    # Convert to seconds as the auth_time in the token claims is in seconds.
    revocation_second = user.tokens_valid_after_timestamp / 1000
    return 'Tokens revoked at: {0}'.format(revocation_second)