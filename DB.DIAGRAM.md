# 📊 Modelo de Base de Datos
```mermaid
erDiagram
    MEDIA ||--o{ MILESTONE : tiene
    MEDIA ||--o{ CHARACTER : contiene
    
    MEDIA {
        int id
        string title
    }
    MILESTONE {
        int id
        int media_id
        string description
    }