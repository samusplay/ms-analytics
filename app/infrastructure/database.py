import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# ✔ leer variable correctamente
DATABASE_URL = os.getenv("DATABASE_URL")

print("DATABASE_URL:", DATABASE_URL)  # 👈 DEBUG

if not DATABASE_URL:
    raise Exception("DATABASE_URL no está configurada")

# ✔ Conexión a la base de datos
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ✔ verificar conexión
def check_db_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"\033[91m❌ Error crítico conectando a la BD: {e}\033[0m")
        return False


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()