import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

def determinar_tipo_manga(row):
    synopsis = str(row.get('synopsis', '')).lower()
    type_field = str(row.get('type', '')).lower()
    if 'manhwa' in type_field or 'manhwa' in synopsis or 'webtoon' in synopsis:
        return 'Manhwa'
    if 'manhua' in type_field or 'manhua' in synopsis:
        return 'Manhua'
    return 'Manga'

def cargar_datos():
    db: Session = SessionLocal()
    chunk_size = 5000
    
    try:
        print("⏳ Procesando cómics e impresos...")
        for chunk in pd.read_csv('data/raw/manga_dataset.csv', chunksize=chunk_size):
            for _, row in chunk.iterrows():
                if not db.query(models.Media).filter(models.Media.title == row['title']).first():
                    nuevo_medio = models.Media(
                        title=row['title'],
                        type=determinar_tipo_manga(row),
                        tropes=row.get('genres', None),
                        status=row.get('status', 'Unknown'),
                        episodes_count=row.get('chapters', 0)  # Total capítulos
                    )
                    db.add(nuevo_medio)
            db.commit()

        print("⏳ Procesando animación y Live Actions...")
        for chunk in pd.read_csv('data/raw/anime_dataset.csv', chunksize=chunk_size):
            for _, row in chunk.iterrows():
                if not db.query(models.Media).filter(models.Media.title == row['title']).first():
                    # Detectar si es una adaptación Live Action registrada en MAL
                    es_live_action = str(row.get('source', '')).lower() == 'live action'
                    
                    nuevo_anime = models.Media(
                        title=row['title'],
                        type='Live Action' if es_live_action else 'Anime',
                        tropes=row.get('genres', None),
                        status=row.get('status', 'Unknown'),
                        episodes_count=row.get('episodes', 0)
                    )
                    db.add(nuevo_anime)
            db.commit()
            
        print("🚀 ¡Importación transmedia masiva completada con éxito!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cargar_datos()