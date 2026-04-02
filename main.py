from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import certifi

# ================== LOAD ENV ==================
load_dotenv()

# ================== FASTAPI ==================
app = FastAPI()

# ================== CORS (FIXED) ==================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://student-ai-dashboard-frontend.vercel.app",
        "https://student-ai-dashboard-frontend-git-main-abhis-projects-66a94381.vercel.app",
        "https://student-ai-dashboard-frontend-1fwk2bvvt-abhis-projects-66a94381.vercel.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Handle preflight requests explicitly (important for Render/Vercel)
@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return {"message": "Preflight OK"}

# ================== MONGODB ==================
MONGO_URL = os.getenv("MONGO_URL")

client_db = MongoClient(
    MONGO_URL,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client_db["student_db"]
collection = db["students"]

# Create unique index
try:
    collection.create_index("id", unique=True)
except Exception as e:
    print("Index creation / DB error:", e)

# ================== GROQ ==================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ================== MODELS ==================
class Prompt(BaseModel):
    message: str

class Student(BaseModel):
    id: int
    name: str
    course: str

# ================== ROUTES ==================
@app.get("/")
def home():
    return {"message": "API is running 🚀"}

@app.post("/chat")
def chat(prompt: Prompt):
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt.message}],
            model="llama-3.3-70b-versatile",
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/students")
def create_student(student: Student):
    try:
        collection.insert_one(student.dict())
        return {"message": "Student created ✅"}
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Student with this ID already exists"
        )

@app.get("/students")
def get_students():
    students = []
    for s in collection.find():
        s["_id"] = str(s["_id"])
        students.append(s)
    return students

@app.put("/students/{id}")
def update_student(id: int, student: Student):
    result = collection.update_one(
        {"id": id},
        {"$set": {"name": student.name, "course": student.course}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student updated ✅"}

@app.delete("/students/{id}")
def delete_student(id: int):
    result = collection.delete_one({"id": id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted ✅"}