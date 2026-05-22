from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    type = Column(String)  # Anime / Manga
    # Para el "Culture & Tropes Encyclopedia"
    tropes = Column(String) # Ej: "Tsundere, White Hair, Enemies to Lovers"
    aesthetic = Column(String) # Ej: "90s Cyberpunk, Neon Pastel"
    
    # Relación con hitos (para el Spoiler Control)
    milestones = relationship("Milestone", back_populates="owner")

class Milestone(Base):
    __tablename__ = "milestones"
    id = Column(Integer, primary_key=True)
    description = Column(String) # Ej: "Muerte de X", "Revelación de traición"
    chapter_occurrence = Column(Integer) # En qué capítulo pasa
    is_spoiler = Column(Boolean, default=True)
    media_id = Column(Integer, ForeignKey("media.id"))
    
    owner = relationship("Media", back_populates="milestones")