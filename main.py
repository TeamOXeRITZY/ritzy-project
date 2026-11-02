from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import uvicorn

# --- DATABASE CONFIGURATION ---
DATABASE_URL = "sqlite:///./ritzy.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- SQLALCHEMY MODELS ---
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    bio = Column(String)
    profile_pic = Column(String)

class PostDB(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_url = Column(String)
    caption = Column(String)
    likes = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

# --- PYDANTIC MODELS ---
class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    bio: str
    profile_pic: str

class PostCreate(BaseModel):
    """Schema for creating a post (no ID needed)"""
    user_id: int
    content_url: str
    caption: str
    likes: Optional[int] = 0

class PostSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    content_url: str
    caption: str
    likes: int

# --- DEPENDENCY ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- FASTAPI APP ---
app = FastAPI(title="Ritzy API", description="Backend for Ritzy with SQLite")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Ritzy API!", "database": "SQLite active"}

@app.get("/feed", response_model=List[PostSchema])
async def get_feed(db: Session = Depends(get_db)):
    return db.query(PostDB).all()

@app.get("/user/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/user", response_model=UserSchema)
async def create_user(username: str, bio: str, profile_pic: str, db: Session = Depends(get_db)):
    new_user = UserDB(username=username, bio=bio, profile_pic=profile_pic)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/post", response_model=PostSchema)
async def create_post(post: PostCreate, db: Session = Depends(get_db)):
    """Saves a post using the PostCreate schema so the ID is auto-generated."""
    db_post = PostDB(**post.model_dump())
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
