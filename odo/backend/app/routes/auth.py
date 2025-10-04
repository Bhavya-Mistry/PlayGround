from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

from .. import services
from ..config import get_database, Database
from ..models.company import CompanyModel
from ..models.user import UserModel, UserRole
from ..schemas.user import UserOut, Token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

class SignUpRequest(BaseModel):
    """Defines the required data for a new company and admin signup."""
    company_name: str
    company_currency: str # e.g., "USD", "INR"
    full_name: str
    email: EmailStr
    username: str
    password: str

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(request: SignUpRequest, db: Database = Depends(get_database)):
    """
    Handles the creation of a new company and its primary admin user.
    This is the first step for any new organization using the system.
    """
    # Check if user already exists
    existing_user = db.users.find_one({"$or": [{"email": request.email}, {"username": request.username}]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists."
        )

    # 1. Create the new company
    new_company = CompanyModel(name=request.company_name, default_currency=request.company_currency)
    created_company = db.companies.insert_one(new_company.model_dump(by_alias=True))

    # 2. Create the admin user for that company
    hashed_password = services.auth_service.get_password_hash(request.password)
    new_user = UserModel(
        company_id=created_company.inserted_id,
        full_name=request.full_name,
        email=request.email,
        username=request.username,
        hashed_password=hashed_password,
        role=UserRole.ADMIN, # The first user is always an Admin
        is_active=True
    )
    created_user = db.users.insert_one(new_user.model_dump(by_alias=True))
    
    # Retrieve the full user document to return
    user_doc = db.users.find_one({"_id": created_user.inserted_id})
    return user_doc


@router.post("/token", response_model=Token)
def login_for_access_token(db: Database = Depends(get_database), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticates a user and returns a JWT access token.
    Uses the standard OAuth2 password flow.
    """
    user_doc = db.users.find_one({"username": form_data.username})

    # Validate user and password
    if not user_doc or not services.auth_service.verify_password(form_data.password, user_doc["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = UserModel(**user_doc)
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    # Create and return the access token
    access_token = services.auth_service.create_access_token(
        data={"sub": user.username, "role": user.role.value}
    )
    return {"access_token": access_token, "token_type": "bearer"}