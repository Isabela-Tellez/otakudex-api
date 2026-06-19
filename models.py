from database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String 
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # Clave encriptada
    is_active = Column(Boolean, default=True)

    # Relación: Un usuario es dueño de muchos registros de media
    items = relationship("Media", back_populates="owner")

# Tabla intermedia para el Grafo de Relaciones Transmedia (M:N)
class MediaRelation(Base):
    __tablename__ = "media_relations"
    
    source_id = Column(Integer, ForeignKey("media.id", ondelete="CASCADE"), primary_key=True)
    target_id = Column(Integer, ForeignKey("media.id", ondelete="CASCADE"), primary_key=True)
    relation_type = Column(String, default="Adaptación") # Ej: "Adaptación", "Precuela", "Secuela"

class Media(Base):
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)  # Estricto: "Anime", "Manga", "Manhwa" o "Manhua"
    
    # Para el "Culture & Tropes Encyclopedia"
    tropes = Column(String) # Ej: "Tsundere, White Hair, Enemies to Lovers"
    aesthetic = Column(String) # Ej: "90s Cyberpunk, Neon Pastel"
    
    # Vínculo con el Usuario dueño del registro
    owner_id = Column(Integer, ForeignKey("users.id")) 
    owner = relationship("User", back_populates="items")
    
    # Relación con hitos (para el Spoiler Control)
    milestones = relationship("Milestone", back_populates="owner")

    # Relación autoreferencial para conectar formatos cruzados (Ecosistema Transmedia)
    related_to = relationship(
        "Media",
        secondary="media_relations",
        primaryjoin="Media.id==MediaRelation.source_id",
        secondaryjoin="Media.id==MediaRelation.target_id",
        backref="related_from"
    )

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
    death_chapter = Column(Integer, nullable=True) # Si es nulo, sigue vivo
    
    owner = relationship("Media")