from database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String 
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)  
    is_active = Column(Boolean, default=True)

    items = relationship("Media", back_populates="owner")

# Tabla intermedia para el Grafo de Relaciones Transmedia (M:N)
class MediaRelation(Base):
    __tablename__ = "media_relations"
    
    source_id = Column(Integer, ForeignKey("media.id", ondelete="CASCADE"), primary_key=True)
    target_id = Column(Integer, ForeignKey("media.id", ondelete="CASCADE"), primary_key=True)
    relation_type = Column(String, default="Adaptación") 

class Media(Base):
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)  # "Anime", "Manga", "Manhwa", "Manhua", "Live Action"
    
    # Nuevas columnas requeridas para el dataset 2026
    status = Column(String, default="Unknown")
    episodes_count = Column(Integer, default=0)
    
    # Para el "Culture & Tropes Encyclopedia"
    tropes = Column(String) 
    aesthetic = Column(String) 
    
    # Vínculo con el Usuario
    owner_id = Column(Integer, ForeignKey("users.id")) 
    owner = relationship("User", back_populates="items")
    
    # [AÑADIDO AQUÍ] Relación con las alertas de Spoilers / Eventos críticos
    events = relationship("MediaEvent", back_populates="media", cascade="all, delete-orphan")

    # Relación autoreferencial (Ecosistema Transmedia)
    related_to = relationship(
        "Media",
        secondary="media_relations",
        primaryjoin="Media.id==MediaRelation.source_id",
        secondaryjoin="Media.id==MediaRelation.target_id",
        backref="related_from"
    )

class MediaEvent(Base):
    __tablename__ = "media_events"
    id = Column(Integer, primary_key=True, index=True)
    media_id = Column(Integer, ForeignKey("media.id", ondelete="CASCADE"))
    episode_or_chapter = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)  # Ej: "Muerte", "Gore", "Giro de trama"
    description = Column(String, nullable=False)
    is_spoiler = Column(Boolean, default=True)

    # Relación inversa hacia Media
    media = relationship("Media", back_populates="events")

class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    media_id = Column(Integer, ForeignKey("media.id", ondelete="CASCADE"))
    death_chapter = Column(Integer, nullable=True) 
    
    media_owner = relationship("Media")