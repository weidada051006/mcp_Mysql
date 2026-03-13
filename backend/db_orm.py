from .models import Product, SessionLocal


def add_product(name: str, price: float, stock: int) -> str:
    """添加商品"""
    session = SessionLocal()
    try:
        product = Product(name=name, price=price, stock=stock)
        session.add(product)
        session.commit()
        return f"成功添加商品：名称：{name}，价格：{price}，库存：{stock}"
    except Exception:
        session.rollback()
        return "添加失败，请检查输入数据。"
    finally:
        session.close()


def delete_product(product_id: int) -> str:
    """删除商品"""
    session = SessionLocal()
    try:
        product = session.get(Product, product_id)
        if product:
            session.delete(product)
            session.commit()
            return f"成功删除ID为{product_id}的商品"
        else:
            return f"未找到ID为{product_id}的商品"
    except Exception:
        session.rollback()
        return "删除失败"
    finally:
        session.close()


def delete_product_by_name(name: str) -> str:
    """根据商品名称模糊删除"""
    if not name or not name.strip():
        return "未提供商品名称"
    session = SessionLocal()
    try:
        products = session.query(Product).filter(Product.name.like(f"%{name.strip()}%")).all()
        count = len(products)
        for p in products:
            session.delete(p)
        session.commit()
        if count > 0:
            return f"成功删除名称包含「{name}」的商品，共 {count} 条。"
        return f"未找到名称包含「{name}」的商品。"
    except Exception:
        session.rollback()
        return "删除失败"
    finally:
        session.close()


def update_product(product_id: int, name: str = None, price: float = None, stock: int = None) -> str:
    """更新商品信息"""
    session = SessionLocal()
    try:
        product = session.get(Product, product_id)
        if not product:
            return f"未找到ID为{product_id}的商品"
        if name is not None:
            product.name = name
        if price is not None:
            product.price = price
        if stock is not None:
            product.stock = stock
        session.commit()
        return f"成功更新ID为{product_id}的商品"
    except Exception:
        session.rollback()
        return "更新失败"
    finally:
        session.close()


def query_products(
    condition: str = None,
    price_min: float = None,
    price_max: float = None,
    stock_min: int = None,
    stock_max: int = None,
    return_count_only: bool = False,
) -> str:
    """查询商品"""
    session = SessionLocal()
    try:
        query = session.query(Product)
        if condition:
            query = query.filter(Product.name.like(f"%{condition}%"))
        if price_min is not None:
            query = query.filter(Product.price >= price_min)
        if price_max is not None:
            query = query.filter(Product.price <= price_max)
        if stock_min is not None:
            query = query.filter(Product.stock >= stock_min)
        if stock_max is not None:
            query = query.filter(Product.stock <= stock_max)

        if return_count_only:
            count = query.count()
            return f"符合条件的商品共 {count} 个。"

        products = query.all()
        if not products:
            return "没有找到匹配的商品"
        lines = ["查询结果："]
        for p in products:
            lines.append(f"名称：{p.name}，价格：{p.price}，库存：{p.stock}")
        return "\n".join(lines)
    except Exception:
        return "查询失败"
    finally:
        session.close()


def add_products(products: list) -> str:
    """批量添加多个商品，products 为 [{"name","price","stock"}, ...]"""
    if not products:
        return "未提供要添加的商品列表"
    session = SessionLocal()
    try:
        objs = []
        for item in products:
            name = item.get("name")
            price = item.get("price")
            stock = item.get("stock")
            if name is None or price is None or stock is None:
                continue
            objs.append(Product(name=name, price=float(price), stock=int(stock)))
        if objs:
            session.add_all(objs)
            session.commit()
            return f"成功批量添加 {len(objs)} 个商品。"
        return "没有成功添加任何商品（请检查每项是否包含 name、price、stock）"
    except Exception:
        session.rollback()
        return "批量添加失败"
    finally:
        session.close()


def delete_products(product_ids: list) -> str:
    """批量根据ID删除商品"""
    if not product_ids:
        return "未提供要删除的商品ID列表"
    session = SessionLocal()
    try:
        deleted = (
            session.query(Product).filter(Product.id.in_(product_ids)).delete(synchronize_session=False)
        )
        session.commit()
        return f"成功删除 {deleted} 个商品（ID: {product_ids}）。"
    except Exception:
        session.rollback()
        return "批量删除失败"
    finally:
        session.close()
