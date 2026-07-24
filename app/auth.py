from urllib.parse import urljoin, urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from . import db
from .forms import LoginForm, RegisterForm
from .models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def is_safe_redirect_url(target):
    if not target:
        return False
    host_url = request.host_url
    return urlparse(urljoin(host_url, target)).netloc == urlparse(host_url).netloc


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("products.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()

        if User.query.filter_by(username=username).first():
            flash("이미 사용 중인 아이디입니다.", "danger")
            return render_template("register.html", form=form)

        user = User(username=username)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash("회원가입이 완료되었습니다. 로그인해 주세요.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("products.index"))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(form.password.data):
            flash("아이디 또는 비밀번호가 올바르지 않습니다.", "danger")
            return render_template("login.html", form=form)

        login_user(user)
        next_url = request.args.get("next")
        if next_url and is_safe_redirect_url(next_url):
            return redirect(next_url)

        return redirect(url_for("products.index"))

    return render_template("login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()
    flash("로그아웃되었습니다.", "info")
    return redirect(url_for("products.index"))
