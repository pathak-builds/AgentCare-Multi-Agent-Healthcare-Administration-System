from fastapi import Depends, HTTPException, status, Request
from app.auth.dependencies import get_current_user_from_cookie

def require_role_web(*allowed_roles: str):
    def role_checker(request: Request, current_user = Depends(get_current_user_from_cookie)):
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        return current_user
    return role_checker