from passlib.context import CryptContext

# Configuramos el algoritmo de encriptación (bcrypt es el estándar)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    """Convierte la contraseña plana en un hash seguro para la DB."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """Comprueba si la contraseña ingresada coincide con el hash guardado."""
    return pwd_context.verify(plain_password, hashed_password)