import mysql.connector
from db_connection import get_connection


def add_product(name: str, price: float, stock: int) -> str:
    """添加商品"""
    conn = get_connection()
    if not conn:
        return "数据库连接失败"
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
            (name, price, stock)
        )
        conn.commit()
        product_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return f"成功添加商品：{name}，ID为{product_id}"
    except Exception as e:
        return f"添加失败：{str(e)}"


def delete_product(product_id: int) -> str:
    """删除商品"""
    conn = get_connection()
    if not conn:
        return "数据库连接失败"
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        if affected > 0:
            return f"成功删除ID为{product_id}的商品"
        else:
            return f"未找到ID为{product_id}的商品"
    except Exception as e:
        return f"删除失败：{str(e)}"


def delete_product_by_name(name: str) -> str:
    """根据商品名称删除商品（名称模糊匹配，会删除所有匹配到的商品）"""
    if not name or not name.strip():
        return "未提供商品名称"
    conn = get_connection()
    if not conn:
        return "数据库连接失败"
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE name LIKE %s", (f"%{name.strip()}%",))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        if affected > 0:
            return f"成功删除名称包含「{name}」的商品，共 {affected} 条。"
        return f"未找到名称包含「{name}」的商品。"
    except Exception as e:
        return f"删除失败：{str(e)}"


def update_product(product_id: int, name: str = None, price: float = None, stock: int = None) -> str:
    """更新商品信息（至少提供一个更新字段）"""
    if name is None and price is None and stock is None:
        return "未提供任何更新字段"
    conn = get_connection()
    if not conn:
        return "数据库连接失败"
    try:
        cursor = conn.cursor()
        updates = []
        params = []
        if name is not None:
            updates.append("name = %s")
            params.append(name)
        if price is not None:
            updates.append("price = %s")
            params.append(price)
        if stock is not None:
            updates.append("stock = %s")
            params.append(stock)
        params.append(product_id)
        sql = f"UPDATE products SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(sql, params)
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        if affected > 0:
            return f"成功更新ID为{product_id}的商品"
        else:
            return f"未找到ID为{product_id}的商品"
    except Exception as e:
        return f"更新失败：{str(e)}"


def query_products(
    condition: str = None,
    price_min: float = None,
    price_max: float = None,
    stock_min: int = None,
    stock_max: int = None,
    return_count_only: bool = False
) -> str:
    """查询商品：支持按名称模糊、价格区间、库存区间筛选；return_count_only 为 True 时只返回数量"""
    conn = get_connection()
    if not conn:
        return "数据库连接失败"
    try:
        cursor = conn.cursor(dictionary=True)
        where_parts = []
        params = []
        if condition:
            where_parts.append("name LIKE %s")
            params.append(f"%{condition}%")
        if price_min is not None:
            where_parts.append("price >= %s")
            params.append(price_min)
        if price_max is not None:
            where_parts.append("price <= %s")
            params.append(price_max)
        if stock_min is not None:
            where_parts.append("stock >= %s")
            params.append(stock_min)
        if stock_max is not None:
            where_parts.append("stock <= %s")
            params.append(stock_max)
        sql = "SELECT * FROM products"
        if where_parts:
            sql += " WHERE " + " AND ".join(where_parts)
        cursor.execute(sql, params)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        if return_count_only:
            return f"符合条件的商品共 {len(results)} 个。"
        if not results:
            return "没有找到匹配的商品"
        lines = ["查询结果："]
        for row in results:
            lines.append(f"ID: {row['id']}, 名称: {row['name']}, 价格: {row['price']}, 库存: {row['stock']}")
        return "\n".join(lines)
    except Exception as e:
        return f"查询失败：{str(e)}"


def add_products(products: list) -> str:
    """批量添加多个商品，products 为 [{"name","price","stock"}, ...]"""
    if not products:
        return "未提供要添加的商品列表"
    conn = get_connection()
    if not conn:
        return "数据库连接失败"
    try:
        cursor = conn.cursor()
        added = []
        for item in products:
            name = item.get("name")
            price = item.get("price")
            stock = item.get("stock")
            if name is None or price is None or stock is None:
                continue
            cursor.execute(
                "INSERT INTO products (name, price, stock) VALUES (%s, %s, %s)",
                (name, float(price), int(stock))
            )
            added.append((name, cursor.lastrowid))
        conn.commit()
        cursor.close()
        conn.close()
        if not added:
            return "没有成功添加任何商品（请检查每项是否包含 name、price、stock）"
        lines = [f"成功批量添加 {len(added)} 个商品："]
        for name, pid in added:
            lines.append(f"  - {name}，ID为{pid}")
        return "\n".join(lines)
    except Exception as e:
        return f"批量添加失败：{str(e)}"


def delete_products(product_ids: list) -> str:
    """批量根据 ID 删除多个商品"""
    if not product_ids:
        return "未提供要删除的商品ID列表"
    conn = get_connection()
    if not conn:
        return "数据库连接失败"
    try:
        cursor = conn.cursor()
        deleted = 0
        for pid in product_ids:
            cursor.execute("DELETE FROM products WHERE id = %s", (int(pid),))
            deleted += cursor.rowcount
        conn.commit()
        cursor.close()
        conn.close()
        return f"成功删除 {deleted} 个商品（ID: {product_ids}）。"
    except Exception as e:
        return f"批量删除失败：{str(e)}"
