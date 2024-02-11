import os
import databases
import sqlalchemy
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load
from fastapi.middleware.cors import CORSMiddleware

load()

DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)

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
print(notes)

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
async def create_note(note: NoteIn):
    pass
    try:
        #Generating the query
        query = notes.insert().values(
            title=note.title,
            description=note.description,
        )
        # Keep in mind that the execute method returns the ID of the created record
        record_id = await database.execute(query)
        #retrieving the created note
        created_note_query =  notes.select().where(notes.c.id == record_id)
        created_note = await database.fetch_one(created_note_query)
        
        print(created_note)
        return {
            **created_note.model_dump(),
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/notes/")
async def read_notes(skip: int = 0, take: int = 20):
    query = notes.select()
    notes_to_change = await database.fetch_all(query)
    # notes to change convert to dict()
    notes_to_change = [dict(note) for note in notes_to_change]
    return  {"notes": notes_to_change, "total": len(notes_to_change)}

@app.get("/notes/{note_id}")
async def read_note(note_id: int):
    query = notes.select().where(notes.c.id == note_id)
    return await database.fetch_one(query)

@app.put("/notes/{note_id}")
async def update_note(note_id: int, note: NoteIn):
    query = notes.update().where(notes.c.id == note_id).values(
        title=note.title,
        description=note.description
    )
    await database.execute(query)
    return {**note.dict(), "id": note_id}

@app.delete("/notes/{note_id}")
async def delete_note(note_id: int):
    query = notes.delete().where(notes.c.id == note_id)
    await database.execute(query)
    return {"message": "Note with id: {} deleted successfully!".format(note_id)}

@app.get("/")
def read_root():
    return {"Hello": "World"}