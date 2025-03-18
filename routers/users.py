import sys
sys.path.append("..")

from starlette import status
from starlette.responses import RedirectResponse
from fastapi import Depends, APIRouter, Request, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user, bcrypt_context
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix='/users',
    tags=['users'],
    responses={401: {"description": "Not Found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

class UserVerify(BaseModel):
    username: str
    password: str
    new_password: str

@router.get('/edit_password', response_class=HTMLResponse)
async def user_edit(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("edit_user_password.html", {"request": request, "user": user})

@router.post('/edit_password', response_class=HTMLResponse)
async def user_edit(request: Request, db: Session = Depends(get_db),
                      username: str = Form(...), password: str = Form(...), new_password: str = Form(...)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    user_model = db.query(models.Users).filter(models.Users.username == username).first()
    msg = "Invalid username or password"
    if user_model and bcrypt_context.verify(password, user_model.hashed_password):
        user_model.hashed_password = bcrypt_context.hash(new_password)
        db.add(user_model)
        db.commit()
        msg = "Password updated successfully."
    return templates.TemplateResponse("edit_user_password.html", {"request": request, "user": user, "msg": msg})
