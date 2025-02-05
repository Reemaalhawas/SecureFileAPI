from fastapi import FastAPI
from datetime import datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException
from Databases import get_mysql_connection, password_hasher
from fastapi import HTTPException
from fastapi import File, UploadFile
import shutil


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


@app.post("/signup/")
def create_account(username: str, email: str, password: str):
    conn = get_mysql_connection()
    cursor = conn.cursor()

    hashed_pw = password_hasher.hash(password)

    try:
        cursor.execute("INSERT INTO users (username, email, hashed_password) VALUES (%s, %s, %s)", 
                       (username, email, hashed_pw))
        conn.commit()
    except:
        raise HTTPException(status_code=400, detail="Username or email already taken.")
    finally:
        cursor.close()
        conn.close()

    return {"message": "User successfully registered"}


@app.post("/login/")
def authenticate_user(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, hashed_password FROM users WHERE username = %s", (form_data.username,))
    user_data = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user_data or not password_hasher.verify(form_data.password, user_data[1]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = generate_jwt(payload={"sub": form_data.username, "user_id": user_data[0]})
    return {"access_token": access_token, "token_type": "bearer"}


UPLOAD_FOLDER = Path("user_uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), token: str = Depends(token_auth)):
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    user_id = payload.get("user_id")

    file_path = UPLOAD_FOLDER / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = file_path.stat().st_size

    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO uploaded_files (file_name, file_size, file_path, uploaded_by) VALUES (%s, %s, %s, %s)",
                   (file.filename, file_size, str(file_path), user_id))
    conn.commit()
    cursor.close()
    conn.close()

    return {"filename": file.filename, "size": file_size, "message": "File uploaded successfully"}


