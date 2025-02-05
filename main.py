from fastapi import FastAPI
from datetime import datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

@app.get("/")
def home():
    return {"message": "File Storage API is running"}



JWT_SECRET = ""  
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRATION_MINUTES = 30

def generate_jwt(payload: dict, expires_delta: timedelta = None):
    expiry = datetime.utcnow() + (expires_delta or timedelta(minutes=TOKEN_EXPIRATION_MINUTES))
    payload.update({"exp": expiry})
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)



token_auth = OAuth2PasswordBearer(tokenUrl="login")


