from fastapi import FastAPI
import uvicorn
from routes.auth_routes import router as auth_router
from routes.contractor_route import router as contractor_router
from routes.govt_agent_route import router as govt_agent_router
from routes.inspection_officer_route import router as inspection_officer_router
from routes.user_route import router as user_router

app = FastAPI(
    title="Government Fraud Detection System",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(contractor_router)
app.include_router(govt_agent_router)
app.include_router(inspection_officer_router)
app.include_router(user_router)


@app.get("/")
def health_check():
    return {
        "message": "Government Fraud Detection System API Running"
    }

if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )