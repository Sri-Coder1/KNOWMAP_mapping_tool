from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from pathlib import Path
import json
import requests
import urllib.parse
import xml.etree.ElementTree as ET

# =========================
# NLP IMPORTS
# =========================
from .nlp.preprocessing import preprocess_text
from .nlp.ner import extract_entities
from .nlp.relation_extraction import extract_relations
from .nlp.triples import build_triples
from .nlp.graph_builder import build_graph, graph_to_json
from .nlp.cross_domain import detect_cross_domain

# =========================
# APP CONFIG
# =========================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_path = Path(__file__).parent.parent / "frontend"

SECRET_KEY = "knowmap_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# =========================
# DATABASE
# =========================

DATABASE_URL = "sqlite:///./knowmap.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    interests = Column(String)


class UserGraph(Base):
    __tablename__ = "user_graphs"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    source = Column(String)
    topic = Column(String)
    entities_json = Column(Text)
    cross_links_json = Column(Text)
    graph_json = Column(Text)
    created_at = Column(String)


Base.metadata.create_all(bind=engine)

# =========================
# PASSWORD HASHING
# =========================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


def validate_password(password: str):
    import re
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[!@#$%^&*]", password)
    )

# =========================
# JWT
# =========================

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(auth_header: str):
    if not auth_header:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# =========================
# SCHEMAS
# =========================

class RegisterSchema(BaseModel):
    username: str
    email: EmailStr
    password: str
    interests: list[str]


class LoginSchema(BaseModel):
    username: str
    password: str


class FetchSchema(BaseModel):
    source: str
    topic: str


class ProcessSchema(BaseModel):
    source: str
    topic: str
    content: str

# =========================
# DB DEPENDENCY
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# AUTH ROUTES
# =========================

@app.post("/register")
def register(user: RegisterSchema, db: Session = Depends(get_db)):

    existing = db.query(User).filter(
        (User.username == user.username) |
        (User.email == user.email)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    if not validate_password(user.password):
        raise HTTPException(status_code=400, detail="Weak password")

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
        interests=",".join(user.interests)
    )

    db.add(new_user)
    db.commit()

    return {"message": "Registered successfully"}


@app.post("/login")
def login(user: LoginSchema, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(
        (User.username == user.username) |
        (User.email == user.username)
    ).first()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.username})

    return {"access_token": token}

# =========================
# FETCH EXTERNAL DATA
# =========================

@app.post("/fetch-external")
def fetch_external(data: FetchSchema):

    source = data.source.lower()
    topic = urllib.parse.quote(data.topic.strip())

    if source == "wikipedia":
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{topic}"
        response = requests.get(url)

        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Wikipedia page not found")

        wiki = response.json()
        return {"content": wiki.get("extract", "")}

    elif source == "arxiv":
        url = f"http://export.arxiv.org/api/query?search_query=all:{topic}&max_results=5"
        response = requests.get(url)

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="arXiv fetch failed")

        root = ET.fromstring(response.text)
        summaries = []

        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            summary = entry.find('{http://www.w3.org/2005/Atom}summary')
            if summary is not None:
                summaries.append(summary.text.strip())

        return {"content": "\n\n".join(summaries)}

    elif source == "kaggle":
        # Placeholder (real Kaggle API requires credentials)
        return {
            "content": f"Kaggle dataset related to {data.topic}. "
                       f"This dataset contains structured data useful for cross-domain mapping."
        }

    else:
        raise HTTPException(status_code=400, detail="Invalid source")

# =========================
# FILE UPLOAD
# =========================

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    text = content.decode("utf-8", errors="ignore")
    return {"content": text}

# =========================
# PROCESS DATA
# =========================

@app.post("/process-data")
def process_data(data: ProcessSchema,
                 Authorization: str = Header(None),
                 db: Session = Depends(get_db)):

    username = verify_token(Authorization)

    text = preprocess_text(data.content)

    entities = extract_entities(text)
    relations = extract_relations(text)
    triples = build_triples(relations)

    graph = build_graph(triples)
    graph_json = graph_to_json(graph)

    cross_links = detect_cross_domain(triples)

    new_graph = UserGraph(
        username=username,
        source=data.source,
        topic=data.topic,
        entities_json=json.dumps(entities),
        cross_links_json=json.dumps(cross_links),
        graph_json=json.dumps(graph_json),
        created_at=str(datetime.utcnow())
    )

    db.add(new_graph)
    db.commit()
    db.refresh(new_graph)

    return {
        "graph_id": new_graph.id,
        "entities": entities,
        "cross_domain_links": cross_links,
        "graph": graph_json
    }

# =========================
# LOAD SAVED GRAPHS
# =========================

@app.get("/my-graphs")
def get_user_graphs(Authorization: str = Header(None),
                    db: Session = Depends(get_db)):

    username = verify_token(Authorization)

    graphs = db.query(UserGraph).filter(
        UserGraph.username == username
    ).order_by(UserGraph.id.desc()).all()

    return [
        {
            "id": g.id,
            "source": g.source,
            "topic": g.topic,
            "entities": json.loads(g.entities_json),
            "cross_links": json.loads(g.cross_links_json),
            "graph": json.loads(g.graph_json),
            "created_at": g.created_at
        }
        for g in graphs
    ]

# =========================
# GET SINGLE GRAPH
# =========================

@app.get("/graph/{graph_id}")
def get_single_graph(graph_id: int,
                     Authorization: str = Header(None),
                     db: Session = Depends(get_db)):

    username = verify_token(Authorization)

    graph = db.query(UserGraph).filter(
        UserGraph.id == graph_id,
        UserGraph.username == username
    ).first()

    if not graph:
        raise HTTPException(status_code=404, detail="Graph not found")

    return {
        "entities": json.loads(graph.entities_json),
        "cross_domain_links": json.loads(graph.cross_links_json),
        "graph": json.loads(graph.graph_json)
    }

# =========================
# FRONTEND SERVING
# =========================

@app.get("/")
async def root():
    return FileResponse(str(frontend_path / "login.html"))

app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")
