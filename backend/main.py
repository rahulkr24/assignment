from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import os
from sqlalchemy.orm import declarative_base

from dotenv import load_dotenv
import openai
import json

# Load environment variables
load_dotenv()

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



# Change this line:
Base = declarative_base()

# SQLAlchemy Todo model
class TodoModel(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class TodoBase(BaseModel):
    title: str
    description: str
    completed: bool = False
    due_date: Optional[datetime] = None

class TodoCreate(TodoBase):
    pass

class Todo(TodoBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# AI Service
class AIService:
    def __init__(self):
        self.provider = os.getenv("AI_PROVIDER", "openai")
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        
        if self.provider == "openai":
            # Use the new OpenAI client syntax
            self.client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
            )
    
    async def generate_summary(self, todos: List[Todo]) -> str:
        if not todos:
            return "No tasks to summarize."
        
        # Prepare todos for AI
        todos_data = []
        for todo in todos:
            status = "completed" if todo.completed else "pending"
            due_info = f", due on {todo.due_date.strftime('%Y-%m-%d')}" if todo.due_date else ""
            todos_data.append(f"- {todo.title}: {status}{due_info}")
        
        todos_text = "\n".join(todos_data)
        
        if self.provider == "openai":
            try:
                # Use the new OpenAI API syntax
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes todo lists."},
                        {"role": "user", "content": f"Please provide a concise summary of these tasks:\n{todos_text}"}
                    ],
                    max_tokens=150
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"AI summary unavailable: {str(e)}"
        else:
            # Fallback summary
            completed = sum(1 for todo in todos if todo.completed)
            pending = len(todos) - completed
            return f"You have {len(todos)} tasks: {completed} completed, {pending} pending."

ai_service = AIService()

# API endpoints
@app.post("/todos/", response_model=Todo)
async def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = TodoModel(**todo.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo
    

@app.get("/todos/", response_model=List[Todo])
async def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    todos = db.query(TodoModel).offset(skip).limit(limit).all()
    return todos

@app.get("/todos/{todo_id}", response_model=Todo)
async def read_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.put("/todos/{todo_id}", response_model=Todo)
async def update_todo(todo_id: int, todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    for key, value in todo.dict().items():
        setattr(db_todo, key, value)
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}", response_model=Todo)
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(todo)
    db.commit()
    return todo


@app.get("/todos/summary", response_model=str)
async def get_summary(db: Session = Depends(get_db)):
    try:
        todos = db.query(TodoModel).all()
        
        # Use a simple approach without Pydantic conversion
        completed = sum(1 for todo in todos if todo.completed)
        pending = len(todos) - completed
        
        if len(todos) == 0:
            return "No tasks to summarize."
        elif len(todos) == 1:
            status = "completed" if todos[0].completed else "pending"
            return f"You have 1 task: '{todos[0].title}' is {status}."
        else:
            return f"You have {len(todos)} tasks: {completed} completed, {pending} pending."
            
    except Exception as e:
        return f"Error generating summary: {str(e)}"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)