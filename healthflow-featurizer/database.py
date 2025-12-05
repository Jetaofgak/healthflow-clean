from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
# Remplace avec tes infos : user:password@localhost:port/dbname

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5433/healthflow_ms"  # valeur par défaut pour ton PC
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Fonction utilitaire pour avoir une session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

