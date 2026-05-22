from database import Base
from sqlalchemy import Column, Integer, String, Boolean

class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    type = Column(String)  # Anime o Manga
    tropes = Column(String) # Ej: "Isekai, OP Protagonist"
    safe_chapter = Column(Integer, default=0) # Por dónde se va en el anime
    is_completed = Column(Boolean, default=False)