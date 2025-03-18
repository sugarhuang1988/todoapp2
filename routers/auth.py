# 导入必要的库和模块
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Form # FastAPI 相关组件
from models import Users  # 用户模型，假设在 models.py 中定义
from passlib.context import CryptContext  # 密码加密/验证工具
from typing import Annotated, Optional  # 类型提示
from sqlalchemy.orm import Session  # SQLAlchemy 数据库会话
from database import SessionLocal  # 数据库连接对象
from starlette import status  # HTTP 状态码
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer  # OAuth2 认证相关
from jose import jwt, JWTError  # JWT 编码/解码工具
from datetime import timedelta, datetime  # 时间处理
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse

# 创建一个路由实例，指定前缀为 '/auth'，并添加标签 'auth'
router = APIRouter(
    prefix='/auth',
    tags=['auth'],
    responses={401: {"description": "Not authorized"}}
)

class LoginForm:
    def __init__(self, request: Request):
        # request: Request 作为 LoginForm 类的初始化参数，用于存储当前请求对象。
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        # create_oauth_form 方法通过 self.request.form() 获取request中的表单数据。
        form = await self.request.form()
        self.username = form.get("username")
        self.password = form.get("password")

# 定义密钥和算法用于 JWT 编码/解码
SECRET_KEY = "1cf7534bbebde996c95fcb262370090b3235aaccbf9af521b0e8d38d0a0c9890"
ALGORITHM = "HS256"

# 初始化密码加密上下文
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_bearer 是一个 OAuth2PasswordBearer 实例
# 它会在tokenUrl="auth/token"路由位置请求头中提取 JWT 令牌。
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

# 获取数据库会话的生成器函数
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

# 定义一个依赖项，用于获取数据库会话
db_dependency = Annotated[Session, Depends(get_db)]

# 创建一个 Jinjia2Templates 实例，用于渲染模板
templates = Jinja2Templates(directory="templates")

# 验证用户身份的函数
def authentication_check(username, password, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

# 创建访问令牌的函数
def create_access_token(username: str, user_id: int, user_role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': user_role}
    expire = datetime.utcnow() + expires_delta
    encode.update({'exp': expire})
    # 返回生成的访问令牌token
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# 获取当前用户的异步函数，通过 JWT 解码获取用户信息
async def get_current_user(request: Request):
    try:
        token = request.cookies.get('access_token')
        if token is None:
            return None
        # 使用 JWT 解码token获取用户信息
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        # 如果用户信息为空，则抛出异常；如果用户信息不为空，则返回用户信息
        if username is None or user_id is None:
            logout(request)
        return {'username': username, 'id': user_id, 'role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

# 登录页面的路由
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, db: db_dependency):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

        token_response = await login_for_access_token(form_data=form, db=db)

        if not token_response:
            msg = "Incorrect Username or Password"
            return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

        response.set_cookie(key="access_token", value=token_response.get("access_token"), httponly=True)
        return response
    except HTTPException:
        msg = "Unknown Error"
        return templates.TemplateResponse("login.html", {"request": request, "msg": msg})

@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    msg = "Logout Successfully"
    response = templates.TemplateResponse("login.html", {"request": request, "msg": msg})
    response.delete_cookie(key="access_token")
    return response

# 注册页面的路由
@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register_user(request: Request, db: db_dependency,
                        email: str = Form(...), username: str = Form(...),
                        firstname: str = Form(...),lastname: str = Form(...),
                        password: str = Form(...), password2: str = Form(...)):
    email_check = db.query(Users).filter(Users.email == email).first()
    username_check = db.query(Users).filter(Users.username == username).first()
    if email_check:
        return templates.TemplateResponse("register.html", {"request": request, "msg": "Email already registered"})
    if username_check:
        return templates.TemplateResponse("register.html", {"request": request, "msg": "Username already registered"})
    if password != password2:
        return templates.TemplateResponse("register.html", {"request": request, "msg": "Passwords do not match"})

    new_user = Users(
        email=email,
        username=username,
        first_name=firstname,
        last_name=lastname,
        hashed_password=bcrypt_context.hash(password),
        role="user",
        is_active=True,
        phone_number=None
    )

    db.add(new_user)
    db.commit()

    return templates.TemplateResponse("login.html", {"request": request, "msg": "User Successfully Registered, Please Sign in!"})


@router.post("/token")
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: db_dependency):
    user = authentication_check(form_data.username, form_data.password, db)
    if not user:
        return False
    token = create_access_token(user.username, user.id, user.role, expires_delta=timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}



