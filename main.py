
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from groq import Groq
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import certifi

# Load ENV
load_dotenv()

# ================== MONGODB (GLOBAL) ==================
MONGO_URL = os.getenv("MONGO_URL")

client_db = MongoClient(
    MONGO_URL,
    tls=True,
    tlsCAFile=certifi.where()
)

db = client_db["student_db"]
collection = db["students"]


# Create unique index (prevents duplicate IDs)
try:
    collection.create_index("id", unique=True)
except Exception as e:
    print("Index creation / DB error:", e)

# ================== FASTAPI ==================
app = FastAPI()

# ================== CORS ==================
origins = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# 🤖 AI Chat
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


# 🎓 CREATE
@app.post("/students")
def create_student(student: Student):
    try:
        collection.insert_one(student.dict())
        return {"message": "Student created ✅"}
    except Exception:
        raise HTTPException(status_code=400, detail="Student with this ID already exists")


# 📄 READ
@app.get("/students")
def get_students():
    students = []
    for s in collection.find():
        s["_id"] = str(s["_id"])
        students.append(s)
    return students


# ✏️ UPDATE
@app.put("/students/{id}")
def update_student(id: int, student: Student):
    result = collection.update_one(
        {"id": id},
        {"$set": {"name": student.name, "course": student.course}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student updated ✅"}


# 🗑 DELETE
@app.delete("/students/{id}")
def delete_student(id: int):
    result = collection.delete_one({"id": id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student deleted ✅"}



















#  Main Code 

# from fastapi  import FastAPI
# from pydantic import BaseModel
# from groq import Groq
# import os 
# from dotenv import load_dotenv
# from fastapi.middleware.cors import CORSMiddleware
# from pymongo import MongoClient

# # MongoDB Connection
# client_db = MongoClient("mongodb://localhost:27017/")
# db = client_db["student_db"]
# collection = db["students"]


# load_dotenv()

# app = FastAPI()


# # ✅ CORS FIX
# origins = [
#     "http://127.0.0.1:5500",
#     "http://localhost:5500",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,   # frontend URLs
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )



# client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# # Propmpt Class
# class Prompt(BaseModel):
#     message:str


# # Student Class
# class Student(BaseModel):
#     id: int
#     name: str
#     course: str




# @app.get("/")
# def home():
#     return {"message": "Groq API is running 🚀"}


# # Groq AI

# @app.post("/chat")
# def chat(prompt:Prompt):
#     response = client.chat.completions.create(
#     messages=[
#         {
#             "role": "user",
#             "content": prompt.message,
#         }
#     ],
#     model="llama-3.3-70b-versatile",
# )
#     return {"response" : response.choices[0].message.content}


# # Students 
# @app.post("/students")
# def create_student(student: Student):
#     collection.insert_one(student.dict())
#     return {"message": "Student created"}


# @app.get("/students")
# def get_students():
#     students = []
#     for s in collection.find():
#         s["_id"] = str(s["_id"])  # convert ObjectId to string
#         students.append(s)
#     return students


# @app.put("/students/{id}")
# def update_student(id: int, student: Student):
#     result = collection.update_one(
#         {"id": id},
#         {"$set": {"name": student.name, "course": student.course}}
#     )

#     if result.modified_count == 0:
#         return {"message": "Student not found"}

#     return {"message": "Student updated"}


# @app.delete("/students/{id}")
# def delete_student(id: int):
#     result = collection.delete_one({"id": id})

#     if result.deleted_count == 0:
#         return {"message": "Student not found"}

#     return {"message": "Student deleted"}