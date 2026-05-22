# 🏗️ Arquitectura del Sistema

```mermaid
graph TD
    User((Usuario)) --> API[FastAPI Server]
    API --> Schema{Pydantic Schemas}
    Schema --> ORM[SQLAlchemy ORM]
    ORM --> DB[(otakudex.db)]
    
    style User fill:#f9f,stroke:#333,stroke-width:2px
    style DB fill:#00ff,stroke:#333,stroke-width:2px