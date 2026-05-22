from pydantic import BaseModel
from typing import Optional, List

# Esquemas para la creación de usuarios (Se recibe la contraseña)
class UserCreate(BaseModel):
    username: str
    password: str

# Esquema para mostrar usuario (¡SIN CONTRASEÑA!)
class UserOut(BaseModel):
    id: int
    username: str
    is_active: bool

    class config:
        from_attributes = True

# --- ESQUEMAS PARA HITOS (SPOILERS) ---
class MilestoneBase(BaseModel):
    description: str
    chapter_occurrence: int
    is_spoiler: bool = True

class MilestoneCreate(MilestoneBase):
    pass

class MilestoneResponse(MilestoneBase):
    id: int
    media_id: int

    class Config:
        from_attributes = True

# --- ESQUEMAS PARA ANIME/MANGA ---
class MediaCreate(BaseModel):
    title: str
    type: str  # Anime o Manga
    tropes: Optional[str] = None # Ej: "Tsundere, Enemies to Lovers"
    aesthetic: Optional[str] = None # Ej: "90s Cyberpunk"
    safe_chapter: int = 0

class MediaResponse(MediaCreate):
    id: int
    is_completed: bool
    # Esto permite que cuando se consulte un anime, se puedan ver sus spoilers si se quiere
    milestones: List[MilestoneResponse] = []

    class Config:
        from_attributes = True