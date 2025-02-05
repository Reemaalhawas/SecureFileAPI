import mysql.connector
from passlib.context import CryptContext

password_hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="admin",
        password="securepassword123",
        database="file_storage_db"
    )
