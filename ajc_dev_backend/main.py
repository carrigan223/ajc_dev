import os
import databases
import sqlalchemy
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

notes = sqlalchemy.Table(
    "notes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String(length=255)),
    sqlalchemy.Column("description", sqlalchemy.Text),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)
# look into this deeper
# metadata.create_all(engine)

class NoteIn(BaseModel):
    title: str
    description: str
    
class Note(BaseModel):
    id: int
    title: str
    description: str
    created_at: str
    updated_at: str


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()
    
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    
@app.post("/notes/", response_model=Note)
async def create_note(note):
    print(note)
    # query = notes.insert().values(title=note.title, description=note.description)
    # last_record_id = await database.execute(query)
    # return {**note.dict(), "id": last_record_id}

@app.get("/notes/", response_model=List[Note])
async def read_notes(skip: int = 0, take: int = 20):
    query = notes.select().offset(skip).limit(take)
    return await database.fetch_all(query)

@app.get("/")
def read_root():
    return {"Hello": "World"}