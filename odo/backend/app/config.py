from pydantic_settings import BaseSettings, SettingsConfigDict
from pymongo import MongoClient
from pymongo.database import Database

class Settings(BaseSettings):
    """
    Manages application settings using Pydantic.
    It automatically reads environment variables from a .env file.
    """
    # MongoDB settings loaded from the .env file
    MONGO_URL: str
    MONGO_DB_NAME: str

    # JWT settings for security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 # Token will be valid for 60 minutes

    # Pydantic settings configuration
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8")

# Create a single, reusable instance of the settings
settings = Settings()

# --- Database Connection ---
# Create a client to connect to your running MongoDB instance
try:
    client = MongoClient(settings.MONGO_URL)
    # You can check if the connection is successful
    client.admin.command('ping')
    print("✅ MongoDB connection successful.")
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")


# Get the database from the client
db = client[settings.MONGO_DB_NAME]

# This is a dependency that we'll use in our API routes
# to get a database session.
def get_database() -> Database:
    return db