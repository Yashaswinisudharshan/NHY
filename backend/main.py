from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routes import budget, departments, complaints, auth

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Government AI System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(departments.router)
app.include_router(budget.router)
app.include_router(complaints.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"status": "Government AI System is running"}