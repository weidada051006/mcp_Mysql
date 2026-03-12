import mysql.connector
from mysql.connector import Error
from config import MYSQL_PASSWORD


def get_connection():
    """获取MySQL数据库连接（使用配置的密码）"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=MYSQL_PASSWORD,
            database='testdb'
        )
        return conn
    except Error as e:
        print(f"连接数据库失败: {e}")
        return None


def init_database():
    """初始化数据库和表（如果不存在）"""
    try:
        # 先连接（不指定数据库）以创建数据库
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password=MYSQL_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS testdb")
        cursor.close()
        conn.close()

        # 连接testdb创建表
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    stock INT NOT NULL
                )
            """)
            # 简单插入一些初始数据
            cursor.execute("SELECT COUNT(*) FROM products")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO products (name, price, stock) VALUES
                    ('苹果', 5.5, 100),
                    ('香蕉', 3.2, 150),
                    ('橙子', 4.0, 80)
                """)
            conn.commit()
            cursor.close()
            conn.close()
            print("数据库初始化完成")
    except Error as e:
        print(f"初始化数据库失败: {e}")


if __name__ == "__main__":
    init_database()
