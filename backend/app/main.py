import json
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
class basicItem(BaseModel):
    username: str
    pwd: str
    dataPack: json

@app.get("/healthcheck")
def healthcheck():
    return {"status": "ok"}

@app.post("/postData")
def push_notification():
    
    return {"message": "Push notification sent"}