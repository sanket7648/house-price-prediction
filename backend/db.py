import os
from sqlalchemy import create_engine, Column, Integer, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# Pull credentials from Hugging Face Secrets securely
DB_USER = os.getenv("DB_USER", "username")
DB_PASS = os.getenv("DB_PASSWORD", "password")
DB_HOST = "mysql-sanket.alwaysdata.net"
DB_NAME = "sanket_house_price_db"

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Match the schema defined in your README
class PredictionRecord(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    med_inc = Column(Float)
    house_age = Column(Float)
    ave_rooms = Column(Float)
    ave_bedrms = Column(Float)
    population = Column(Float)
    ave_occup = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    predicted_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# Auto-create tables on startup
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()