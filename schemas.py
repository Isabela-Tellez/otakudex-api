from pydantic import BaseModel
from typing import Optional

# Lo que el usuario envía cuando crea un anime
class MediaCreate(BaseModel):
    title: str
    type: str  # Anime o Manga
    tropes: Optional[str] = None
    safe_chapter: int = 0

# Lo que la API le devuelve al usuario (incluye el ID de la base de datos)
class MediaResponse(MediaCreate):
    id: int
    is_completed: bool

    class Config:
        from_attributes = True