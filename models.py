from database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String 
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)  #Aqui va la clave encriptada
    is_active = Column(Boolean, default=True)

    # Relación: Un usuario es dueño de muchos registros de media
    items = relationship("Media", back_populates="owner")
class Media(Base):
    __tablename__ = "media"
    owner_id = Column(Integer, ForeignKey("users.id")) #El vínculo
    owner: relationship("User", back_populates="items")
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

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    media_id = Column(Integer, ForeignKey("media.id"))
    death_chapter = Column(Integer, nullable=True) # Si es nulo, sigue vivo en el manga/anime
    
    owner = relationship("Media")