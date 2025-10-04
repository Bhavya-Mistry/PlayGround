from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .. import services
from ..config import get_database, Database
from ..models.user import UserModel, UserRole
from ..schemas.user import UserCreate, UserOut

# --- Router Setup ---
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# --- Dependencies for Security ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Database = Depends(get_database)) -> UserModel:
    """
    Dependency to get the current authenticated user from a token.
    It decodes the token, validates the user, and returns the user model.
    """
    token_data = services.auth_service.decode_access_token(token)
    if not token_data or not token_data.username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_doc = db.users.find_one({"username": token_data.username})
    if user_doc is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return UserModel(**user_doc)

def get_current_admin_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """
    Dependency to ensure the current user is an admin.
    Raises an error if the user does not have the 'admin' role.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user does not have permissions to perform this action."
        )
    return current_user

# --- API Endpoints ---

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Database = Depends(get_database),
    admin_user: UserModel = Depends(get_current_admin_user)
):
    """
    Admin-only endpoint to create a new user (Employee or Manager)
    in the same company as the admin.
    """
    # Check if user already exists
    existing_user = db.users.find_one({"$or": [{"email": user_data.email}, {"username": user_data.username}]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists."
        )

    hashed_password = services.auth_service.get_password_hash(user_data.password)
    new_user = UserModel(
        **user_data.model_dump(exclude={"password"}), # Unpack schema data
        company_id=admin_user.company_id, # Assign to admin's company
        hashed_password=hashed_password
    )

    created_user = db.users.insert_one(new_user.model_dump(by_alias=True))
    user_doc = db.users.find_one({"_id": created_user.inserted_id})
    return user_doc

@router.get("/", response_model=List[UserOut])
def list_users_in_company(
    db: Database = Depends(get_database),
    admin_user: UserModel = Depends(get_current_admin_user)
):
    """
    Admin-only endpoint to list all users in their company.
    """
    user_docs = db.users.find({"company_id": admin_user.company_id})
    return list(user_docs)