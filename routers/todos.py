from fastapi import APIRouter, Depends, HTTPException, Path, Request, Form
from fastapi.responses import Response, HTMLResponse
from starlette import status
from starlette.responses import RedirectResponse
from models import Todos
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from .auth import get_current_user
from fastapi.templating import Jinja2Templates

# 创建一个 FastAPI 路由
router = APIRouter(
    prefix="/todos",
    tags=["todos"],
    responses={404: {"description": "Not found"}}
)

# 创建一个 Jinjia2Templates 实例，用于渲染模板
templates = Jinja2Templates(directory="templates")
def get_db():
    """
    创建并管理数据库会话，确保每个请求都能获得一个新的、独立的数据库会话，
    并在请求结束后自动关闭会话以释放资源。

    Yields:
        Session: 一个 SQLAlchemy 数据库会话对象

    Notes:
        - 使用生成器模式 (`yield`) 和依赖注入 (FastAPI Depends) 确保每次请求都能获取新的会话。
        - `finally` 块确保无论是否发生异常，数据库会话都会被正确关闭，防止连接泄漏。
    """
    db = SessionLocal()  # 创建一个新的数据库会话实例
    try:
        yield db  # 将当前的数据库会话传递给调用者（例如 FastAPI 路由处理函数）
    finally:
        db.close()  # 确保在请求结束时关闭数据库会话，释放资源


@router.get("/", response_class=HTMLResponse)
async def read_all(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
    return templates.TemplateResponse("home.html", {"request": request, "todos": todos, "user": user})

@router.get("/add_todo", response_class=HTMLResponse)
async def add_todo(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("add_todo.html", {"request": request, "user": user})

@router.post("/add_todo", response_class=HTMLResponse)
async def add_todo_post(request: Request, db: Session = Depends(get_db), title: str = Form(...),
                        description: str = Form(...), priority: int = Form(...)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    new_todo = Todos(title=title, description=description, priority=priority, complete=False, owner_id=user.get("id"))
    db.add(new_todo)
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/edit_todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    return templates.TemplateResponse("edit_todo.html", {"request": request, "todo": todo, "user": user})

@router.post("/edit_todo/{todo_id}", response_class=HTMLResponse)
async def edit_todo_post(request: Request, todo_id: int, title: str = Form(...),
                         description: str = Form(...), priority: int = Form(...),
                         db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    todo.title = title
    todo.description = description
    todo.priority = priority
    db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

@router.get("/delete/{todo_id}")
async def delete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model:
        db.query(Todos).filter(Todos.id == todo_id).delete()
        db.commit()

    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)


@router.get("/complete/{todo_id}", response_class=HTMLResponse)
async def complete_todo(request: Request, todo_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        todo_model.complete = not todo_model.complete
        db.commit()
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)