from typing import Annotated
from fastapi import APIRouter, Body, Depends

from dependencies.authentication_handler import get_user_data_from_token
from model.category.category_request_body import CategoryRequestBody
from firebase_admin import firestore

router = APIRouter()

@router.post('/categories')
def add_category(
        category: CategoryRequestBody,
        user: Annotated[any, Depends(get_user_data_from_token)]
    ):

    email = str(user._data["email"])
    db = firestore.client()

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

@router.get('/categories')
def get_categories(
    user: Annotated[any, Depends(get_user_data_from_token)]
):
    
    db = firestore.client()
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

@router.put('/categories')
def update_category(
    request_body: CategoryRequestBody,
    user: Annotated[any, Depends(get_user_data_from_token)]
):
    db = firestore.client()
    
    doc_ref = db.collection("Categories/{}/data".format(str(user.uid))).document(request_body.id)
    request_body.set_update_time()
    doc_ref.update(request_body.to_dict())

    return {
        'category': doc_ref.get().to_dict(),
        'message': 'success'
    }

@router.delete('/categories')
def delete_category(
    ids: Annotated[list, Body()],
    user: Annotated[any, Depends(get_user_data_from_token)]
):
    db = firestore.client()
    
    for category_id in ids:
        doc_ref = db.collection("Categories/{}/data".format(str(user.uid))).document(str(category_id))
        doc_ref.delete()

    return 'success'