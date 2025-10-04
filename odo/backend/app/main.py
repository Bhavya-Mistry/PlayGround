from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all router objects
from .routes import auth
from .routes import users
from .routes import expenses
from .routes import approvals # <--- ADD THIS LINE

# Create the FastAPI app instance
app = FastAPI(
    title="Expense Management System API",
    description="API for managing company expenses and approval workflows.",
    version="1.0.0"
)

# --- Middleware ---
# Configure CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routers ---
# Include all the routers for our API
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(expenses.router)
app.include_router(approvals.router) # <--- ADD THIS LINE

# --- Root Endpoint ---
@app.get("/", tags=["Root"])
def read_root():
    """
    Welcome endpoint for the API.
    """
    return {"message": "Welcome to the Expense Management System API"}