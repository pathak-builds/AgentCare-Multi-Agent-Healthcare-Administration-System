from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.services.auth_service import AuthService
from app.auth.jwt import set_token_cookie, decode_access_token
from app.repositories.user_repository import UserRepository

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# ---------------------------------------------------------
# Home Page
# ---------------------------------------------------------

@router.get("/")
def home(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Home page.

    If user already has a valid login cookie,
    redirect to the appropriate dashboard.

    Otherwise show the landing page.
    """

    user = None

    token = request.cookies.get("access_token")

    if token:
        try:
            payload = decode_access_token(token)

            repo = UserRepository(db)

            user = repo.get_by_id(payload["sub"])

        except Exception:
            user = None

    if user:

        if user.role == "patient":
            return RedirectResponse(
                url="/patient/dashboard",
                status_code=303,
            )

        if user.role in ("admin", "hospital_staff"):
            return RedirectResponse(
                url="/admin/dashboard",
                status_code=303,
            )

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
        },
    )


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

@router.get("/login")
def login_page(request: Request):

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "user": None,
        },
    )


@router.post("/login")
def login_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    try:
        data = service.login(email, password)

    except HTTPException:

        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "user": None,
                "error": "Invalid email or password.",
            },
        )

    response = RedirectResponse(
        url="/patient/dashboard",
        status_code=303,
    )

    set_token_cookie(
        response,
        data["access_token"],
    )

    return response


# ---------------------------------------------------------
# Register
# ---------------------------------------------------------

@router.get("/register")
def register_page(request: Request):

    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "user": None,
        },
    )


@router.post("/register")
def register_post(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    try:
        data = service.register(
            email=email,
            password=password,
            full_name=full_name,
        )

    except HTTPException as e:

        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "user": None,
                "error": e.detail,
            },
        )

    response = RedirectResponse(
        url="/patient/dashboard",
        status_code=303,
    )

    set_token_cookie(
        response,
        data["access_token"],
    )

    return response


# ---------------------------------------------------------
# Logout
# ---------------------------------------------------------

@router.get("/logout")
def logout():

    response = RedirectResponse(
        url="/",
        status_code=303,
    )

    response.delete_cookie("access_token")

    return response