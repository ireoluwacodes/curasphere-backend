from fastapi import APIRouter, Depends
from typing import Mapping

from src.api.deps import get_current_user
from src.api.user.models import User
from src.api.user.service import UserService
from src.api.user.schema import UserUpdateInput
from src.api.user.dependency import get_user

router = APIRouter()


@router.get("/")
async def read_users(
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_user),
):
    users = user_service.get_users()
    return users


@router.get("/{user_id}")
async def read_user(
    user_id: int,
    user_service: UserService = Depends(),
    user: Mapping = Depends(get_user),
    current_user: User = Depends(get_current_user),
):
    user = user_service.get_user(user_id)
    return user


@router.put("/update/{user_id}")
async def update_user(
    user_id: int,
    user_update_input: UserUpdateInput,
    user_service: UserService = Depends(),
    user: Mapping = Depends(get_user),
    current_user: User = Depends(get_current_user),
):
    user = user_service.update_user(user_id, user_update_input)
    return user


@router.delete("/delete/{user_id}")
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(),
    current_user: User = Depends(get_current_user),
):
    user = user_service.delete(user_id)
    return user
