from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List

# --- DATABASE SETUP ---
DATABASE_URL = "sqlite:///./monster_hunter.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- MODELS ---
class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    actor_name = Column(String)
    role_description = Column(String)

Base.metadata.create_all(bind=engine)

# --- SCHEMAS (Pydantic) ---
class CharacterSchema(BaseModel):
    id: int
    name: str
    actor_name: str
    role_description: str

    class Config:
        from_attributes = True

# --- APP INITIALIZATION ---
app = FastAPI(title="Monster Hunter Movie API")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- SEED DATA (Internal logic to populate SQLite on first run) ---
def seed_db():
    db = SessionLocal()
    if db.query(Character).count() == 0:
        data = [
            Character(name="Natalie Artemis", actor_name="Milla Jovovich", role_description="US Army Ranger Captain"),
            Character(name="The Hunter", actor_name="Tony Jaa", role_description="Skilled warrior of the New World"),
            Character(name="The Admiral", actor_name="Ron Perlman", role_description="Leader of the Hunter group"),
            Character(name="Lincoln", actor_name="T.I.", role_description="Member of Artemis's squad"),
            Character(name="Dash", actor_name="Meagan Good", role_description="Squad medic and soldier")
        ]
        db.add_all(data)
        db.commit()
    db.close()

seed_db()

# --- ROUTES ---

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Monster Hunter (2020) Fanbase API"}

@app.get("/characters", response_model=List[CharacterSchema], tags=["Characters"])
def get_all_characters(db: Session = Depends(get_db)):
    """1. Get All Characters"""
    return db.query(Character).all()

@app.get("/characters/{char_id}", response_model=CharacterSchema, tags=["Characters"])
def get_character(char_id: int, db: Session = Depends(get_db)):
    """2. Get a Specific Character"""
    char = db.query(Character).filter(Character.id == char_id).first()
    if not char:
        raise HTTPException(status_code=404, detail="Character not found")
    return char

@app.get("/actors", tags=["Actors"])
def get_actors(db: Session = Depends(get_db)):
    """3. Get Actors"""
    characters = db.query(Character).all()
    return [{"actor": c.actor_name, "plays": c.name} for c in characters]