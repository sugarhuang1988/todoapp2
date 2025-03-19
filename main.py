from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import models
from database import engine
from routers import todos, auth, users
import uvicorn
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from starlette import status

# 创建 FastAPI 应用程序
app = FastAPI()

# 创建所有基于 Base 类 在 models 中定义的数据类，并映射到数据库中构建对应数据表（如果它们还不存在）
# Base 是 SQLAlchemy 的声明基类，包含了所有模型类的元数据
# metadata.create_all 方法会根据模型类的定义生成相应的 SQL 语句来创建表结构
# bind 参数指定了要使用的数据库引擎，在这里使用的是之前创建的 engine 实例
models.Base.metadata.create_all(bind=engine)

# 创建静态文件路由
# 这段代码用于将静态文件（如CSS、JavaScript、图片等）挂载到FastAPI应用中，使其可以通过指定的URL路径访问。
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/', response_class=HTMLResponse)
async def root():
    return RedirectResponse(url="/todos", status_code=status.HTTP_302_FOUND)

# 注册路由
app.include_router(todos.router)
app.include_router(auth.router)
app.include_router(users.router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8090)