from typing import List

from fastapi import Depends, HTTPException

from src.api.deps import get_current_user
from src.api.user.models import User, UserRole


class RoleCheck:
    def __init__(self, roles: List[UserRole]) -> None:
        self.required_roles = roles

    def __call__(self, user: User = Depends(get_current_user)) -> bool:
        if user.role not in self.required_roles:
            raise HTTPException(status_code=401, detail="Not authorized")
        return True
