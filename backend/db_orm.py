"""
基于 SQLAlchemy 的商品管理模块：增删改查及批量操作。
使用会话上下文管理器统一管理连接，捕获 SQLAlchemy 异常并记录日志。
"""
import logging
from contextlib import contextmanager
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError

from .models import Product, SessionLocal

logger = logging.getLogger(__name__)


@contextmanager
def session_scope():
    """会话上下文：自动关闭 session，提交/回滚由调用方在 with 内完成。"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _validate_price(price: Optional[float]) -> Optional[str]:
    if price is None:
        return None
    if price <= 0:
        return "价格必须大于 0"
    return None


def _validate_stock(stock: Optional[int]) -> Optional[str]:
    if stock is None:
        return None
    if stock < 0:
        return "库存不能为负数"
    return None


def add_product(name: str, price: float, stock: int) -> str:
    """添加商品（校验价格>0、库存>=0）"""
    err = _validate_price(price) or _validate_stock(stock)
    if err:
        return err
    with session_scope() as session:
        try:
            product = Product(name=name, price=price, stock=stock)
            session.add(product)
            session.commit()
            return f"成功添加商品：名称：{name}，价格：{price}，库存：{stock}"
        except SQLAlchemyError as e:
            session.rollback()
            logger.error("添加商品失败: %s", e, exc_info=True)
            return "添加失败，请检查输入数据。"


def delete_product(product_id: int) -> str:
    """根据 ID 删除商品"""
    with session_scope() as session:
        try:
            product = session.get(Product, product_id)
            if product:
                session.delete(product)
                session.commit()
                return f"成功删除ID为{product_id}的商品"
            return f"未找到ID为{product_id}的商品"
        except SQLAlchemyError as e:
            session.rollback()
            logger.error("删除商品失败: %s", e, exc_info=True)
            return "删除失败"


def delete_product_by_name(name: str) -> str:
    """根据商品名称模糊删除（批量 DELETE，不加载到内存）"""
    if not name or not name.strip():
        return "未提供商品名称"
    keyword = name.strip()
    with session_scope() as session:
        try:
            deleted_count = (
                session.query(Product)
                .filter(Product.name.like(f"%{keyword}%"))
                .delete(synchronize_session=False)
            )
            session.commit()
            if deleted_count > 0:
                return f"成功删除名称包含「{keyword}」的商品，共 {deleted_count} 条。"
            return f"未找到名称包含「{keyword}」的商品。"
        except SQLAlchemyError as e:
            session.rollback()
            logger.error("按名称删除商品失败: %s", e, exc_info=True)
            return "删除失败"


def update_product(
    product_id: int,
    name: str = None,
    price: float = None,
    stock: int = None,
) -> str:
    """更新商品信息（可选校验价格、库存）"""
    if name is None and price is None and stock is None:
        return "未提供任何更新字段"
    err = _validate_price(price) or _validate_stock(stock)
    if err:
        return err
    with session_scope() as session:
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
        except SQLAlchemyError as e:
            session.rollback()
            logger.error("更新商品失败: %s", e, exc_info=True)
            return "更新失败"


def query_products(
    condition: str = None,
    price_min: float = None,
    price_max: float = None,
    stock_min: int = None,
    stock_max: int = None,
    return_count_only: bool = False,
) -> str:
    """查询商品（多条件组合，可选仅返回数量）"""
    with session_scope() as session:
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
        except SQLAlchemyError as e:
            logger.error("查询商品失败: %s", e, exc_info=True)
            return "查询失败"


def add_products(products: List[dict]) -> str:
    """批量添加商品；返回成功数与被跳过数（缺失或无效的项会被跳过）"""
    if not products:
        return "未提供要添加的商品列表"
    with session_scope() as session:
        try:
            objs: List[Product] = []
            skipped = 0
            for item in products:
                name = item.get("name")
                price = item.get("price")
                stock = item.get("stock")
                if name is None or price is None or stock is None:
                    skipped += 1
                    continue
                try:
                    p, s = float(price), int(stock)
                except (ValueError, TypeError):
                    skipped += 1
                    continue
                if p <= 0 or s < 0:
                    skipped += 1
                    continue
                objs.append(Product(name=name, price=p, stock=s))
            if objs:
                session.add_all(objs)
                session.commit()
                if skipped:
                    return f"成功批量添加 {len(objs)} 个商品，{skipped} 个项被跳过（数据无效或格式错误）。"
                return f"成功批量添加 {len(objs)} 个商品。"
            return f"没有成功添加任何商品（共 {skipped} 个项数据无效）。"
        except SQLAlchemyError as e:
            session.rollback()
            logger.error("批量添加商品失败: %s", e, exc_info=True)
            return "批量添加失败"


def delete_products(product_ids: List[int]) -> str:
    """批量根据 ID 删除商品"""
    if not product_ids:
        return "未提供要删除的商品ID列表"
    with session_scope() as session:
        try:
            deleted = (
                session.query(Product)
                .filter(Product.id.in_(product_ids))
                .delete(synchronize_session=False)
            )
            session.commit()
            return f"成功删除 {deleted} 个商品（ID: {product_ids}）。"
        except SQLAlchemyError as e:
            session.rollback()
            logger.error("批量删除商品失败: %s", e, exc_info=True)
            return "批量删除失败"
