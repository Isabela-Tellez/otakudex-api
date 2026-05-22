from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database

app = FastAPI(title="OtakuDex API")

# Crea las tablas en la base de datos (si Docker está listo)
models.Base.metadata.create_all(bind=database.engine)

# Función para obtener la conexión a la base de datos
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "¡Bienvenido a OtakuDex API!"}

# Ruta para agregar un nuevo anime/manga
@app.post("/media/", response_model=schemas.MediaResponse)
def create_media(item: schemas.MediaCreate, db: Session = Depends(get_db)):
    db_item = models.Media(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

# Ruta para ver todos los animes guardados
@app.get("/media/", response_model=list[schemas.MediaResponse])
def read_all_media(db: Session = Depends(get_db)):
    return db.query(models.Media).all()