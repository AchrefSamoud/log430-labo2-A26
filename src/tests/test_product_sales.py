"""Product sales report backed by Redis."""

from commands.write_order import add_order, delete_order, sync_product_sales_to_redis
from db import get_redis_conn, get_sqlalchemy_session
from models.order import Order
from models.order_item import OrderItem
from queries.read_order import get_best_selling_products
from views.report_view import show_best_sellers


def test_product_sales_follow_order_changes():
    sync_product_sales_to_redis()
    r = get_redis_conn()
    original = {pid: int(r.get(f"product:{pid}") or 0) for pid in (1, 2)}
    order_ids = []

    try:
        order_ids.append(add_order(1, [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 4},
        ]))
        order_ids.append(add_order(1, [{"product_id": 1, "quantity": 3}]))

        assert int(r.get("product:1")) == original[1] + 5
        assert int(r.get("product:2")) == original[2] + 4

        sales = get_best_selling_products()
        assert dict(sales)[1] == original[1] + 5
        assert dict(sales)[2] == original[2] + 4
        assert [quantity for _, quantity in sales] == sorted(
            (quantity for _, quantity in sales), reverse=True
        )
        html = show_best_sellers()
        assert f"Article 1 : {original[1] + 5} vendu(s)" in html
    finally:
        for order_id in reversed(order_ids):
            assert delete_order(order_id) == 1

    assert int(r.get("product:1")) == original[1]
    assert int(r.get("product:2")) == original[2]


def test_existing_order_items_are_counted_on_first_startup():
    r = get_redis_conn()
    previous_count = r.get("product:3")
    previous_marker = r.get("product_sales:initialized")
    session = get_sqlalchemy_session()
    order = None

    try:
        order = Order(user_id=1, total_amount=40.25)
        session.add(order)
        session.flush()
        session.add(OrderItem(order_id=order.id, product_id=3, quantity=7, unit_price=5.75))
        session.commit()

        r.delete("product_sales:initialized")
        sync_product_sales_to_redis()
        expected = int(previous_count or 0) + 7
        assert int(r.get("product:3")) == expected

        sync_product_sales_to_redis()
        assert int(r.get("product:3")) == expected
    finally:
        session.rollback()
        if order is not None and order.id is not None:
            persisted_order = session.get(Order, order.id)
            if persisted_order is not None:
                session.delete(persisted_order)
                session.commit()
        session.close()
        if previous_count is None:
            r.delete("product:3")
        else:
            r.set("product:3", previous_count)
        if previous_marker is None:
            r.delete("product_sales:initialized")
        else:
            r.set("product_sales:initialized", previous_marker)
