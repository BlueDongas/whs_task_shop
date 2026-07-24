from app import db
from app.models import Product, PurchaseRequest

from .conftest import login, logout


def test_other_user_cannot_edit_product(client, users, product):
    login(client, "buyer")
    response = client.get(f"/products/{product}/edit")
    assert response.status_code == 403


def test_other_user_cannot_delete_product(client, users, product):
    login(client, "buyer")
    response = client.post(f"/products/{product}/delete")
    assert response.status_code == 403


def test_seller_cannot_buy_own_product(client, users, product):
    login(client, "seller")
    response = client.post(
        f"/transactions/products/{product}/request",
        follow_redirects=True,
    )
    assert "자신의 상품은 구매 요청할 수 없습니다" in response.get_data(as_text=True)


def test_xss_payload_is_escaped(app, client, users):
    login(client, "seller")
    response = client.post(
        "/products/new",
        data={
            "title": "<script>alert(1)</script>",
            "description": "<img src=x onerror=alert(1)>",
            "price": 1000,
        },
        follow_redirects=True,
    )
    body = response.get_data(as_text=True)
    assert "<script>alert(1)</script>" not in body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body


def test_only_seller_can_accept_request(app, client, users, product):
    login(client, "buyer")
    client.post(f"/transactions/products/{product}/request")
    logout(client)

    with app.app_context():
        req_id = PurchaseRequest.query.filter_by(product_id=product).first().id

    login(client, "buyer")
    response = client.post(f"/transactions/requests/{req_id}/accept")
    assert response.status_code == 403


def test_accept_marks_product_sold_and_rejects_others(app, client, users, product):
    with app.app_context():
        from app.models import User
        another = User(username="buyer2")
        another.set_password("Password1")
        db.session.add(another)
        db.session.commit()

    login(client, "buyer")
    client.post(f"/transactions/products/{product}/request")
    logout(client)

    login(client, "buyer2")
    client.post(f"/transactions/products/{product}/request")
    logout(client)

    with app.app_context():
        requests = PurchaseRequest.query.filter_by(product_id=product).order_by(PurchaseRequest.id).all()
        first_id = requests[0].id

    login(client, "seller")
    response = client.post(f"/transactions/requests/{first_id}/accept", follow_redirects=True)
    assert "판매 완료 처리했습니다" in response.get_data(as_text=True)

    with app.app_context():
        item = db.session.get(Product, product)
        requests = PurchaseRequest.query.filter_by(product_id=product).order_by(PurchaseRequest.id).all()
        assert item.status == Product.STATUS_SOLD
        assert requests[0].status == PurchaseRequest.STATUS_ACCEPTED
        assert requests[1].status == PurchaseRequest.STATUS_REJECTED
