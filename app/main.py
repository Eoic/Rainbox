from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.styles import get_style_by_name
from typing import Dict
from .auth import create_access_token, get_current_user, get_password_hash, verify_password
from .models import User
from .database import get_db
from sqlalchemy.orm import Session
import time

# Rate limiting configuration
RATE_LIMIT_DURATION = 60  # seconds
RATE_LIMIT_REQUESTS = 100  # requests per duration
rate_limit_store: Dict[str, Dict[str, int]] = {}

def check_rate_limit(user_id: str):
    current_time = int(time.time())
    if user_id not in rate_limit_store:
        rate_limit_store[user_id] = {"count": 1, "window_start": current_time}
        return
    
    user_limit = rate_limit_store[user_id]
    if current_time - user_limit["window_start"] >= RATE_LIMIT_DURATION:
        # Reset window
        user_limit["count"] = 1
        user_limit["window_start"] = current_time
    else:
        user_limit["count"] += 1
        if user_limit["count"] > RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Maximum {RATE_LIMIT_REQUESTS} requests per {RATE_LIMIT_DURATION} seconds."
            )

app = FastAPI(title="Rainbox", description="A syntax highlighting web service")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class CodeRequest(BaseModel):
    code: str
    language: str
    theme: str = "default"

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not verify_password(password, str(user.hashed_password)):
        return None
    return user

@app.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User created successfully"}

@app.post("/highlight", response_class=HTMLResponse)
async def highlight_code(request: CodeRequest, current_user: User = Depends(get_current_user)):
    check_rate_limit(str(current_user.id))  # Using the user's id
    try:
        lexer = get_lexer_by_name(request.language)
        style = get_style_by_name(request.theme)
        formatter = HtmlFormatter(style=style, linenos=True, cssclass="source")
        result = highlight(request.code, lexer, formatter)
        css = formatter.get_style_defs('.source')
        html = f"<style>{css}</style>{result}"
        return HTMLResponse(content=html)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
