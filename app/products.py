from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from . import db
from .forms import EmptyForm, ProductForm
from .models import Product, PurchaseRequest

products_bp = Blueprint("products", __name__)


@products_bp.route("/")
def index():
    query = request.args.get("q", "", type=str).strip()
    page = request.args.get("page", 1, type=int)

    stmt = Product.query.order_by(Product.created_at.desc())
    if query:
        pattern = f"%{query}%"
        stmt = stmt.filter(or_(Product.title.ilike(pattern), Product.description.ilike(pattern)))

    pagination = stmt.paginate(page=max(page, 1), per_page=8, error_out=False)
    return render_template(
        "index.html",
        products=pagination.items,
        pagination=pagination,
        query=query,
        empty_form=EmptyForm(),
    )


@products_bp.route("/products/<int:product_id>")
def detail(product_id):
    product = Product.query.get_or_404(product_id)
    existing_request = None
    if current_user.is_authenticated:
        existing_request = PurchaseRequest.query.filter_by(
            product_id=product.id,
            buyer_id=current_user.id,
        ).first()

    return render_template(
        "product_detail.html",
        product=product,
        existing_request=existing_request,
        empty_form=EmptyForm(),
    )


@products_bp.route("/products/new", methods=["GET", "POST"])
@login_required
def create():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            price=form.price.data,
            seller_id=current_user.id,
        )
        db.session.add(product)
        db.session.commit()
        flash("상품이 등록되었습니다.", "success")
        return redirect(url_for("products.detail", product_id=product.id))

    return render_template("product_form.html", form=form, heading="상품 등록")


@products_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit(product_id):
    product = Product.query.get_or_404(product_id)
    if product.seller_id != current_user.id:
        abort(403)

    if product.status == Product.STATUS_SOLD:
        flash("판매 완료된 상품은 수정할 수 없습니다.", "warning")
        return redirect(url_for("products.detail", product_id=product.id))

    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.title = form.title.data.strip()
        product.description = form.description.data.strip()
        product.price = form.price.data
        db.session.commit()
        flash("상품이 수정되었습니다.", "success")
        return redirect(url_for("products.detail", product_id=product.id))

    return render_template("product_form.html", form=form, heading="상품 수정")


@products_bp.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
def delete(product_id):
    form = EmptyForm()
    if not form.validate_on_submit():
        abort(400)

    product = Product.query.get_or_404(product_id)
    if product.seller_id != current_user.id:
        abort(403)

    db.session.delete(product)
    db.session.commit()
    flash("상품이 삭제되었습니다.", "info")
    return redirect(url_for("products.index"))


@products_bp.route("/mypage")
@login_required
def mypage():
    selling_products = Product.query.filter_by(seller_id=current_user.id).order_by(
        Product.created_at.desc()
    ).all()

    buying_requests = PurchaseRequest.query.filter_by(buyer_id=current_user.id).order_by(
        PurchaseRequest.created_at.desc()
    ).all()

    incoming_requests = (
        PurchaseRequest.query.join(Product)
        .filter(Product.seller_id == current_user.id)
        .order_by(PurchaseRequest.created_at.desc())
        .all()
    )

    return render_template(
        "mypage.html",
        selling_products=selling_products,
        buying_requests=buying_requests,
        incoming_requests=incoming_requests,
        empty_form=EmptyForm(),
    )


@products_bp.app_errorhandler(403)
def forbidden(_error):
    return render_template("error.html", code=403, message="이 작업을 수행할 권한이 없습니다."), 403


@products_bp.app_errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="요청한 페이지를 찾을 수 없습니다."), 404


@products_bp.app_errorhandler(413)
def too_large(_error):
    return render_template("error.html", code=413, message="요청 데이터가 너무 큽니다."), 413
