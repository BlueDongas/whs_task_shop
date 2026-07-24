import pytest

from app import create_app, db
from app.models import Product, PurchaseRequest, User


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
            "SECRET_KEY": "test-secret",
        }
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def register(client, username, password="Password1"):
    return client.post(
        "/auth/register",
        data={
            "username": username,
            "password": password,
            "password_confirm": password,
        },
        follow_redirects=True,
    )


def login(client, username, password="Password1"):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def logout(client):
    return client.post("/auth/logout", follow_redirects=True)


@pytest.fixture()
def users(app):
    with app.app_context():
        seller = User(username="seller")
        seller.set_password("Password1")
        buyer = User(username="buyer")
        buyer.set_password("Password1")
        db.session.add_all([seller, buyer])
        db.session.commit()
        return {"seller_id": seller.id, "buyer_id": buyer.id}


@pytest.fixture()
def product(app, users):
    with app.app_context():
        item = Product(
            title="테스트 노트북",
            description="정상 작동합니다.",
            price=500000,
            seller_id=users["seller_id"],
        )
        db.session.add(item)
        db.session.commit()
        return item.id
