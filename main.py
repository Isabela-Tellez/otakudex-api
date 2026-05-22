from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database
import random
from constants import ROAST_DATABASE

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

# --- THE ROAST ENGINE & COMPATIBILITY ---
@app.get("/user/roast/")
def get_user_roast(user_id: int, db: Session = Depends(database.get_db)):
    user_media = db.query(models.Media).all() 
    
    if not user_media:
        return {"roast": "Tu lista está tan vacía como el final de Evangelion. Ve a ver algo antes de pedirme opinión."}

    total = len(user_media)
    shonen_count = len([m for m in user_media if "Shonen" in (m.tropes or "")])
    cyberpunk_count = len([m for m in user_media if "Cyberpunk" in (m.aesthetic or "")])
    romance_count = len([m for m in user_media if "Romance" in (m.tropes or "")])

    # Se elige la categoría del insulto
    if shonen_count / total > 0.6:
        category = "SHONEN_LOVER"
    elif romance_count / total > 0.4:
        category = "ROMANCE_ADDICT"
    else:
        category = "SNOB_PRETENTIOUS"

    # Selecciona un insulto aleatorio de esa categoría en constants.py
    insulto = random.choice(ROAST_DATABASE[category])

    return {
        "level": category.replace("_", " ").title(),
        "roast": insulto
    }

@app.post("/compatibility/compare")
def compare_users(user1_media_ids: List[int], user2_media_ids: List[int]):
    set1 = set(user1_media_ids)
    set2 = set(user2_media_ids)
    
    # Cálculo de Intersección (lo que tienen en común)
    comun = set1.intersection(set2)
    total_universo = set1.union(set2)
    
    # Índice de Jaccard (porcentaje de similitud)
    similitud = (len(comun) / len(total_universo)) * 100 if total_universo else 0
    
    if similitud > 80:
        mensaje = "Son básicamente la misma persona. Casense o peleen a muerte."
    elif similitud > 40:
        mensaje = "Tienen buen potencial de debate. Uno defiende el final y el otro pide un remake."
    else:
        mensaje = "Sus gustos no se tocan ni con un palo. No vean anime juntos por el bien de la amistad."

    return {
        "similarity_score": f"{similitud:.2f}%",
        "common_titles_count": len(comun),
        "verdict": mensaje
    }

@app.get("/user/roast/{user_id}")
def roast_user(user_id: int):
    # (Simulación de lógica de análisis)
    # Aquí podrías contar cuántos "Big Three" tiene el usuario
    return {
        "roast": "Tu top 3 es Naruto, Bleach y One Piece... Tienes la originalidad de un bot de Twitter de 2012. ¿Sabías que existen animes de menos de 500 capítulos?"
    }

# Ruta para ver todos los animes guardados
@app.get("/media/", response_model=list[schemas.MediaResponse])
def read_all_media(db: Session = Depends(get_db)):
    return db.query(models.Media).all()

@app.get("/media/search/", response_model=list[schemas.MediaResponse])
def search_media(trope: str, db: Session = Depends(get_db)):
    # Busca animes que contengan el texto del tropo en su columna 'tropes'
    return db.query(models.Media).filter(models.Media.tropes.contains(trope)).all()

@app.get("/search/culture/")
def search_by_culture(trope: str = None, aesthetic: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Media)
    
    if trope:
        query = query.filter(models.Media.tropes.contains(trope))
    if aesthetic:
        query = query.filter(models.Media.aesthetic.contains(aesthetic))
        
    results = query.all()
    
    if not results:
        return {"message": "No encontramos esa combinación de nicho... quizás eres demasiado original."}
    return results

@app.get("/media/{media_id}/status")
def get_spoiler_safe_status(media_id: int, current_chapter: int, db: Session = Depends(get_db)):
    # Se buscan hitos que ocurran DESPUÉS del capítulo del usuario
    spoilers = db.query(models.Milestone).filter(
        models.Milestone.media_id == media_id,
        models.Milestone.chapter_occurrence > current_chapter
    ).all()
    
    if spoilers:
        return {
            "status": "DANGER",
            "message": f"¡Cuidado! Hay {len(spoilers)} eventos importantes que aún no has visto.",
            "safe_zone": False
        }
    return {"status": "SAFE", "message": "Puedes navegar tranquilo por el fandom.", "safe_zone": True}

# Endpoint para actualizar el capítulo de un anime
@app.patch("/media/{media_id}/chapter", response_model=schemas.MediaResponse)
def update_chapter(media_id: int, new_chapter: int, db: Session = Depends(get_db)):
    # 1. Se busca el registro en la DB
    db_item = db.query(models.Media).filter(models.Media.id == media_id).first()
    
    # 2. Si no existe, se lanza un error 404
    if not db_item:
        raise HTTPException(status_code=404, detail="Anime no encontrado")
    
    # 3. Actualización del valor
    db_item.safe_chapter = new_chapter
    
    # 4. Guardado de cambios
    db.commit()
    db.refresh(db_item)
    return db_item

# Agregar un hito de trama (ej: "Muere tal personaje" en el cap 50)
@app.post("/milestones/", response_model=schemas.MilestoneResponse)
def create_milestone(milestone: schemas.MilestoneCreate, media_id: int, db: Session = Depends(database.get_db)):
    db_milestone = models.Milestone(**milestone.dict(), media_id=media_id)
    db.add(db_milestone)
    db.commit()
    db.refresh(db_milestone)
    return db_milestone

# EL FILTRO MAESTRO: ¿Es seguro ver info de este anime?
@app.get("/media/{media_id}/check-spoiler")
def check_spoiler(media_id: int, user_chapter: int, db: Session = Depends(database.get_db)):
    # Se buscan hitos que el usuario AÚN NO HA VISTO
    spoilers_ahead = db.query(models.Milestone).filter(
        models.Milestone.media_id == media_id,
        models.Milestone.chapter_occurrence > user_chapter
    ).all()
    
    if spoilers_ahead:
        return {
            "safe": False,
            "warning": f"¡ALERTA! Hay {len(spoilers_ahead)} eventos clave después del capítulo {user_chapter}.",
            "count": len(spoilers_ahead)
        }
    return {"safe": True, "message": "Estás al día o no hay eventos registrados aún. ¡Navega seguro!"}

@app.get("/compatibility/group-safety")
def check_group_safety(media_id: int, user_chapters: List[int], db: Session = Depends(database.get_db)):
    # El punto de seguridad es el capítulo del que va más atrás
    slowest_member_chapter = min(user_chapters)
    
    # Se bscan spoilers que estén POR DELANTE del que va más lento
    potential_spoilers = db.query(models.Milestone).filter(
        models.Milestone.media_id == media_id,
        models.Milestone.chapter_occurrence > slowest_member_chapter
    ).all()
    
    return {
        "group_safe_chapter": slowest_member_chapter,
        "danger_zone": len(potential_spoilers) > 0,
        "warning": f"¡Cuidado! El grupo no puede hablar de nada después del capítulo {slowest_member_chapter}." if potential_spoilers else "¡Todos al día! Pueden funar personajes libremente."
    }

@app.get("/characters/{char_id}/status")
def get_character_status(char_id: int, current_chapter: int, db: Session = Depends(database.get_db)):
    char = db.query(models.Character).filter(models.Character.id == char_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Personaje no encontrado")
    
    # Lógica de Spoiler Control:
    if char.death_chapter and current_chapter < char.death_chapter:
        return {"name": char.name, "status": "Vivo/Seguro", "msg": "Puedes buscar fanarts sin miedo."}
    elif char.death_chapter and current_chapter >= char.death_chapter:
        return {"name": char.name, "status": "FALLECIDO", "msg": "¡SPOILER! No entres a TikTok o te vas a deprimir."}
    
    return {"name": char.name, "status": "Vivo", "msg": "Todo despejado."}