from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import router as api_router
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI Interview Coach Backend API",
    version="1.0.0",
)

# Set up CORS middleware to allow requests from Streamlit frontend
origins = [
    "http://localhost",
    "http://localhost:8501", # Default Streamlit port
    "http://localhost:8000", # Default FastAPI port
    # Add your deployed Streamlit URL here when deploying
    # e.g., "https://your-streamlit-app.streamlit.app"
    # For local development, "*" is fine, but restrict it for production.
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Optional: Lifespan events for startup/shutdown
@app.on_event("startup")
async def startup_event():
    print("FastAPI application starting up. Initializing services...")
    # These services are already initialized as singletons upon import,
    # but this hook can be used for other startup tasks if needed.
    # e.g., database connection, loading large static data
    pass

@app.on_event("shutdown")
async def shutdown_event():
    print("FastAPI application shutting down.")
    # Clean up resources if necessary
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)