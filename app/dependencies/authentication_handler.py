from typing import Annotated
from fastapi import HTTPException, Header
from firebase_admin import auth

def get_uid_from_token(Authorization: Annotated[str | None, Header()] = None):
    try:
        token = Authorization.replace('Bearer ','')
        decoded_token = auth.verify_id_token(id_token = token, check_revoked=True)
        return decoded_token['uid']
    except auth.RevokedIdTokenError:
        raise HTTPException(status_code=400, detail="X-Token header invalid")
    except auth.UserDisabledError:
        raise HTTPException(status_code=400, detail="X-Token header invalid")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=400, detail="X-Token header invalid")

def get_user_data_from_token(Authorization: Annotated[str | None, Header()] = None):
    try:
        uid = get_uid_from_token(Authorization)
        return auth.get_user(uid)
    except:
        raise HTTPException(status_code=400, detail="X-Token header invalid")