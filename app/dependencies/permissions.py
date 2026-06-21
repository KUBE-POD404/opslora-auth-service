from fastapi import Depends

from app.dependencies.auth import CurrentUser, get_current_user
from app.exceptions.custom_exception import ForbiddenException


def require_permission(permission: str):
    def permission_checker(current_user: CurrentUser = Depends(get_current_user)):
        if permission not in current_user.permissions:
            raise ForbiddenException("Insufficient permissions")
        return current_user

    return permission_checker
