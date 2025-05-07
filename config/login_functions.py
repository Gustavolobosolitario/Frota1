from database.db_connection import get_connection
from cryptography.fernet import Fernet

def hash_password(password: str, key: bytes):
    f = Fernet(key=key)
    return f.encrypt(password.encode())

def verify_password(stored_password: str, entered_password: str, key: bytes):
    f = Fernet(key=key)
    return f.decrypt(stored_password.encode()).decode() == entered_password

def register_user(email, password, name, key):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
    if cursor.fetchone()[0] > 0:
        cursor.close()
        conn.close()
        return 'Usuário já cadastrado!'
    
    hashed_password = hash_password(password, key)
    cursor.execute("INSERT INTO users (email, password, name) VALUES (%s, %s, %s)", (email, hashed_password, name))
    conn.commit()

    cursor.close()
    conn.close()

    return "Usuário registrado com sucesso!"


def login_user(email, password, key):
    conn = get_connection()
    cursor = conn.cursor()

    # Usar %s como placeholder e passar a variável como argumento
    cursor.execute("SELECT email, password, name FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and verify_password(user[1], password, key):
        return f"Bem-vindo(a), {user[2]}!"
    else:
        return "E-mail ou senha inválidos!"
    
def reset_password(email, new_password, key):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificar se o e-mail existe
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (email,))
    if cursor.fetchone()[0] > 0:
        hashed_password = hash_password(new_password, key)
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_password, email))
        conn.commit()
        cursor.close()
        conn.close()
        return "Senha resetada com sucesso!"
    else:
        cursor.close()
        conn.close()
        return "E-mail não encontrado!"