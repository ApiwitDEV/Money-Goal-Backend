from typing import Annotated
from fastapi import APIRouter, Body, Depends
from model.transaction.transaction_request_body import TransactionRequestBody
from dependencies.authentication_handler import get_uid_from_token, get_user_data_from_token
from firebase_admin import firestore

router = APIRouter()

@router.post("/transactions")
async def add_transaction(
        request_body: Annotated[TransactionRequestBody, Body()],
        user: Annotated[any, Depends(get_user_data_from_token)]
    ):
    email = str(user._data["email"])
    db = firestore.client()
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

@router.get("/transactions")
async def get_transaction(
        user: Annotated[any, Depends(get_user_data_from_token)]
    ):
    db = firestore.client()
    data = []
    for item in db.collection("Transactions/{}/data".format(str(user.uid))).get():
        data.append(item.to_dict())
    return {
        "transactions": data,
        'message': 'success'
    }

@router.put("/transactions")
async def update_transaction(
        request_body: TransactionRequestBody,
        user: Annotated[any, Depends(get_user_data_from_token)]
    ):

    db = firestore.client()
    doc_ref = db.collection("Transactions/{}/data".format(str(user.uid))).document(request_body.id)
    request_body.set_update_time()
    doc_ref.update(request_body.to_dict())
    
    return {
            "transaction": doc_ref.get().to_dict(),
            "message":"success"
        }

@router.delete('/transactions')
async def delete_transaction(
    ids: Annotated[list, Body()],
    user: Annotated[any, Depends(get_user_data_from_token)]
):
    
    db = firestore.client()
    for transaction_id in ids:
        doc_ref = db.collection("Transactions/{}/data".format(str(user.uid))).document(transaction_id)
        doc_ref.delete()

    return 'success'