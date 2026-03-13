"""查看 MySQL 是否可连接，以及 products 表中的数据
运行方式（在项目根目录）：python -m backend.check_db
"""
import sys

from .models import SessionLocal, Product


def main():
    print("正在连接 MySQL (testdb)...")
    session = SessionLocal()
    try:
        rows = session.query(Product).all()
        print("连接成功。")
        if not rows:
            print("表 products 当前无数据。")
            return
        print("\nproducts 表数据：")
        print("-" * 50)
        for r in rows:
            print(f"  ID: {r.id}, 名称: {r.name}, 价格: {r.price}, 库存: {r.stock}")
        print("-" * 50)
        print(f"共 {len(rows)} 条记录。")
    except Exception as e:
        print("连接失败，请确认：1) MySQL 服务已启动  2) 项目根目录 .env 中 MYSQL_PASSWORD 正确")
        print(e)
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
