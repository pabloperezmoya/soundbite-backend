from fastapi import HTTPException, status

from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta

secret_key = "98be74fefe40fc9d993258bf6b7f2e34" # Not a good practice, but it's just a demo

def generate_token(data: dict) -> str:
    dt = datetime.utcnow() + timedelta(minutes=60)
    payload = {
        "email": data['email'],
        "user_id": data['user_id'],
        "exp": dt
    }
    print(dt)
    token: str = encode(
            payload=payload, 
            key=secret_key, 
            algorithm="HS256",
                    )
    return token

def verify_token(token: str) -> dict:
    try:
        data: dict = decode(token, key=secret_key, algorithms=['HS256'])
        return data
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Expired token')
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invañod token')