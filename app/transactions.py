from flask import Blueprint, abort, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from . import db
from .forms import EmptyForm
from .models import Product, PurchaseRequest

transactions_bp = Blueprint("transactions", __name__, url_prefix="/transactions")


def validate_post_form():
    form = EmptyForm()
    if not form.validate_on_submit():
        abort(400)


@transactions_bp.route("/products/<int:product_id>/request", methods=["POST"])
@login_required
def request_purchase(product_id):
    validate_post_form()
    product = Product.query.get_or_404(product_id)

    if product.seller_id == current_user.id:
        flash("자신의 상품은 구매 요청할 수 없습니다.", "danger")
        return redirect(url_for("products.detail", product_id=product.id))

    if product.status != Product.STATUS_SELLING:
        flash("현재 구매할 수 없는 상품입니다.", "warning")
        return redirect(url_for("products.detail", product_id=product.id))

    existing = PurchaseRequest.query.filter_by(
        product_id=product.id,
        buyer_id=current_user.id,
    ).first()
    if existing:
        flash("이미 이 상품에 구매 요청을 보냈습니다.", "warning")
        return redirect(url_for("products.detail", product_id=product.id))

    purchase_request = PurchaseRequest(product_id=product.id, buyer_id=current_user.id)
    db.session.add(purchase_request)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("이미 이 상품에 구매 요청을 보냈습니다.", "warning")
    else:
        flash("구매 요청이 전송되었습니다.", "success")

    return redirect(url_for("products.detail", product_id=product.id))


@transactions_bp.route("/requests/<int:request_id>/accept", methods=["POST"])
@login_required
def accept_request(request_id):
    validate_post_form()
    purchase_request = PurchaseRequest.query.get_or_404(request_id)
    product = purchase_request.product

    if product.seller_id != current_user.id:
        abort(403)

    if purchase_request.status != PurchaseRequest.STATUS_PENDING:
        flash("이미 처리된 요청입니다.", "warning")
        return redirect(url_for("products.mypage"))

    if product.status != Product.STATUS_SELLING:
        flash("이미 판매가 종료된 상품입니다.", "warning")
        return redirect(url_for("products.mypage"))

    purchase_request.status = PurchaseRequest.STATUS_ACCEPTED
    product.status = Product.STATUS_SOLD

    PurchaseRequest.query.filter(
        PurchaseRequest.product_id == product.id,
        PurchaseRequest.id != purchase_request.id,
        PurchaseRequest.status == PurchaseRequest.STATUS_PENDING,
    ).update(
        {PurchaseRequest.status: PurchaseRequest.STATUS_REJECTED},
        synchronize_session=False,
    )

    db.session.commit()
    flash("구매 요청을 승인하고 상품을 판매 완료 처리했습니다.", "success")
    return redirect(url_for("products.mypage"))


@transactions_bp.route("/requests/<int:request_id>/reject", methods=["POST"])
@login_required
def reject_request(request_id):
    validate_post_form()
    purchase_request = PurchaseRequest.query.get_or_404(request_id)

    if purchase_request.product.seller_id != current_user.id:
        abort(403)

    if purchase_request.status != PurchaseRequest.STATUS_PENDING:
        flash("이미 처리된 요청입니다.", "warning")
        return redirect(url_for("products.mypage"))

    purchase_request.status = PurchaseRequest.STATUS_REJECTED
    db.session.commit()
    flash("구매 요청을 거절했습니다.", "info")
    return redirect(url_for("products.mypage"))
