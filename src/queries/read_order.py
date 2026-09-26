"""
Orders (read-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from collections import defaultdict
from db import get_sqlalchemy_session, get_redis_conn
from sqlalchemy import desc
from models.order import Order

def get_order_by_id(order_id):
    """Get order by ID from Redis"""
    r = get_redis_conn()
    return r.hgetall(order_id)

def get_orders_from_mysql(limit=9999):
    """Get last X orders"""
    session = get_sqlalchemy_session()
    return session.query(Order).order_by(desc(Order.id)).limit(limit).all()

def get_orders_from_redis(limit=9999):
    """Get last X orders from Redis, newest first"""
    r = get_redis_conn()
    order_keys = sorted(
        r.scan_iter(match="order:*"),
        key=lambda key: int(key.split(":", 1)[1]),
        reverse=True,
    )[:limit]
    orders = []
    for key in order_keys:
        data = r.hgetall(key)
        orders.append(Order(
            id=int(data["id"]),
            user_id=int(data["user_id"]),
            total_amount=float(data["total_amount"]),
        ))
    return orders

def get_highest_spending_users():
    """Get the ten users who spent the most on orders in Redis"""
    expenses_by_user = defaultdict(float)
    for order in get_orders_from_redis(limit=None):
        expenses_by_user[order.user_id] += order.total_amount
    return sorted(expenses_by_user.items(), key=lambda item: item[1], reverse=True)[:10]
