
# 导入SQLAlchemy所需的库
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 定义数据库连接字符串，这里使用的是SQLite数据库，并且设置为允许跨线程操作
SQLALCHEMY_DATABASE_URI = 'sqlite:///./todosapp.db'

# 连接postgresql
# SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:test12345@localhost/TodoApplicationDataBase'
# engine = create_engine(SQLALCHEMY_DATABASE_URI)

# 创建数据库引擎，通过connect_args参数设置检查同一线程为False以支持多线程
engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})

# 创建会话类，用于与数据库交互。设置autocommit为False表示不会自动提交每个语句，
# 需要显式调用commit()方法；autoflush为False表示不会自动刷新会话中的对象到数据库
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类，所有模型类都将继承自这个基类，它与数据库中的表相对应
Base = declarative_base()
