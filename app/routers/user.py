from fastapi import APIRouter, Body, Form, HTTPException, status
from pydantic import EmailStr
from services.database import DatabaseService

from utils.jwt_manager import generate_token, verify_token
from utils.hash_generator import hash_function

import uuid

router = APIRouter(prefix="/user", tags=["User"])

@router.post(
  path="/login",
  status_code=status.HTTP_200_OK
)
def login(email: str = Form(...), password: str = Form(...)):
  print(email, password)
  # Check if user exists
  resp = DatabaseService().get_user_by_email(email)
  user = [user for user in resp]
  
  if len(user) == 0:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
  
  # Check if password is correct
  if user[0]["password"] != hash_function(password):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

  # Generate token
  token = generate_token({"email": email, "user_id": user[0]["_id"]})
  ## Saving token to database
  DatabaseService().upsert_token(user[0]["_id"], token)
  
  return {
    "email": email,
    "token": token,
    "user_id": user[0]["_id"],
    "name": user[0]["name"],
    }

@router.post(
  path="/verify",
  status_code=status.HTTP_200_OK
)
def verify(token: str = Body(...), user_id: str = Body(...)):
  # Check if user exists
  resp = DatabaseService().get_user_by_id(user_id)
  user = [user for user in resp]
  
  if len(user) == 0:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
  
  if (user[0]["token"] != token):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

  # Check if token is valid  
  try:
    verify_token(token)
  except:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

  return {
    "email": user[0]["email"],
    "token": token,
    "user_id": user[0]["_id"],
    "name": user[0]["name"],
    }


@router.post(
  path="/register",
  status_code=status.HTTP_201_CREATED
)
def register(email: EmailStr = Form(...), name: str = Form(...), password: str = Form(...)):
  # Check if email exists
  resp = DatabaseService().get_user_by_email(email)
  user = [user for user in resp]

  if len(user) != 0:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

  # Hash password
  hashed_password = hash_function(password)

  # Generate user_id
  user_id = uuid.uuid4().hex

  # Generate token
  token = generate_token({"email": email, "user_id": user_id})

  
  # Insert user
  res = DatabaseService().append_user_document({
                                                "_id": user_id,
                                                "email": email, 
                                                "token" : token,
                                                "name": name,
                                                "password": hashed_password, 
                                              })
  if not res.inserted_id:
    raise HTTPException(status_code=500, detail="Error creating user")

  # Return user
  return {
    "user_id": user_id,
    "email": email, 
    "token" : token,
    "name": name
  }
