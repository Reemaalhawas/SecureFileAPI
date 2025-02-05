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

def setup_database():
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(150) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            file_name VARCHAR(255) NOT NULL,
            file_size BIGINT NOT NULL,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT NOT NULL,
            uploaded_by INT NOT NULL,
            FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()
