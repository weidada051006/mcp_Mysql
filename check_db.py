"""查看 MySQL 是否可连接，以及 products 表中的数据"""
import sys
from db_connection import get_connection

def main():
    print("正在连接 MySQL (testdb)...")
    conn = get_connection()
    if not conn:
        print("连接失败，请确认：1) MySQL 服务已启动  2) .env 中 MYSQL_PASSWORD 正确")
        sys.exit(1)
    print("连接成功。")
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    if not rows:
        print("表 products 当前无数据。")
        return
    print("\nproducts 表数据：")
    print("-" * 50)
    for r in rows:
        print(f"  ID: {r['id']}, 名称: {r['name']}, 价格: {r['price']}, 库存: {r['stock']}")
    print("-" * 50)
    print(f"共 {len(rows)} 条记录。")

if __name__ == "__main__":
    main()
