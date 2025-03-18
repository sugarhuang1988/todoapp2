# 导入SQLAlchemy的基类和其他所需的列类型
from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(String)
    # alembic自动生成的迁移脚本会自动添加phone_number字段
    phone_number = Column(String)

# 定义Todos模型类，继承自Base基类
class Todos(Base):
    # 指定该模型类对应的数据库表名为"todos"
    __tablename__ = "todos"

    # 定义id字段，类型为整数，设置为主键并自动索引
    id = Column(Integer, primary_key=True, index=True)

    # 定义title字段，类型为字符串（默认长度为255）
    title = Column(String)

    # 定义description字段，类型为字符串（默认长度为255）
    description = Column(String)

    # 定义priority字段，类型为整数
    priority = Column(Integer)

    # 定义complete字段，类型为布尔值，默认值为False
    complete = Column(Boolean, default=False)

    # 定义owner_id字段，类型为整数，外键关联users表的id字段
    owner_id = Column(Integer, ForeignKey("users.id"))
