from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,EmailStr
from typing import Dict
import uuid
app=FastAPI()
users:Dict[str,dict]={} #using in memory user storage

class User(BaseModel):
    name: str
    email: EmailStr

@app.post("/users") #using post to create a new user
def add_user(user:User):
    user_id=str(uuid.uuid4())
    users[user_id]=user.dict()
    return {"id":user_id,**users[user_id]}

@app.get("/users/{user_id}") #using get to read the users and info
def get_user(user_id:str):
    if user_id not in users:
        raise HTTPException(status_code=404,detail="No user with this user_id exist")
    return {"id":user_id,**users[user_id]}

@app.put("/users/{user_id}") #using put to update the user info
def update_user(user_id:str,updated_user:User):
    if user_id not in users:
        raise HTTPException(status_code=404,detail="No user with this user_id exist")
    users[user_id]=updated_user.dict()
    return {"id":user_id,**users[user_id]}

@app.delete("/users/{user_id}",status_code=204) # to delete an existing user
def delete_user(user_id:str):
    if user_id not in users:
        raise HTTPException(status_code=404,detail="No user with this user_id exist")
    del users[user_id]
    return
