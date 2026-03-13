from sqlalchemy import create_engine, Column, Integer, String, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import MYSQL_PASSWORD

DATABASE_URL = f"mysql+pymysql://root:{MYSQL_PASSWORD or ''}@localhost/testdb"
NO_DB_URL = f"mysql+pymysql://root:{MYSQL_PASSWORD or ''}@localhost/"

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False)


Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """初始化数据库和表（如果不存在），并插入初始数据（表为空时）"""
    try:
        no_db = create_engine(NO_DB_URL)
        with no_db.connect() as conn:
            conn.execute(text("CREATE DATABASE IF NOT EXISTS testdb"))
            conn.commit()
        Base.metadata.create_all(engine)
        session = SessionLocal()
        try:
            if session.query(Product).count() == 0:
                for name, price, stock in [("苹果", 5.5, 100), ("香蕉", 3.2, 150), ("橙子", 4.0, 80)]:
                    session.add(Product(name=name, price=price, stock=stock))
                session.commit()
                print("数据库初始化完成（已插入初始数据）")
        finally:
            session.close()
    except Exception as e:
        print(f"初始化数据库失败: {e}")
