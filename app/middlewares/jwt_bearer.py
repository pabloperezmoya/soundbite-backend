from fastapi.security import HTTPBearer
from fastapi import Request, status, HTTPException
from utils.jwt_manager import verify_token

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = verify_token(auth.credentials)
        if data:
            return data['user_id']
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid token")
