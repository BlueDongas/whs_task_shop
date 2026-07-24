from app.models import User

from .conftest import login, register


def test_register_hashes_password(app, client):
    response = register(client, "newuser")
    assert response.status_code == 200
    assert "회원가입이 완료되었습니다" in response.get_data(as_text=True)

    with app.app_context():
        user = User.query.filter_by(username="newuser").first()
        assert user is not None
        assert user.password_hash != "Password1"
        assert user.check_password("Password1")


def test_duplicate_username_rejected(client):
    register(client, "sameuser")
    response = register(client, "sameuser")
    assert "이미 사용 중인 아이디" in response.get_data(as_text=True)


def test_login_failure_uses_generic_message(client):
    register(client, "loginuser")
    response = login(client, "loginuser", "Wrongpass1")
    assert "아이디 또는 비밀번호가 올바르지 않습니다" in response.get_data(as_text=True)
