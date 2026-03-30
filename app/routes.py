from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app import db
from app.models import Product, ProductImage, Review, ReviewImage
from app.utils import save_uploaded_file, delete_uploaded_file

main = Blueprint("main", __name__)


@main.route("/")
def index():
    products = Product.query.order_by(Product.sort_order.asc(), Product.id.asc()).all()
    reviews = Review.query.order_by(Review.sort_order.asc(), Review.id.asc()).all()
    return render_template("index.html", products=products, reviews=reviews)


@main.route("/admin")
def admin_dashboard():
    products = Product.query.order_by(Product.sort_order.asc(), Product.id.asc()).all()
    return render_template("admin/dashboard.html", products=products)


@main.route("/admin/products/create", methods=["GET", "POST"])
def create_product():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        price_raw = request.form.get("price", "").strip()

        if not title:
            flash("Product title is required.", "error")
            return redirect(url_for("main.create_product"))

        price = None
        if price_raw:
            try:
                price = float(price_raw)
            except ValueError:
                flash("Price must be a valid number.", "error")
                return redirect(url_for("main.create_product"))

        max_sort_order = db.session.query(db.func.max(Product.sort_order)).scalar()
        next_sort_order = (max_sort_order or 0) + 1

        product = Product(
            title=title,
            description=description,
            price=price,
            sort_order=next_sort_order
        )

        db.session.add(product)
        db.session.commit()

        uploaded_files = request.files.getlist("images")
        saved_count = 0

        for index, file in enumerate(uploaded_files, start=1):
            saved_path = save_uploaded_file(file, current_app.config["UPLOAD_FOLDER"])
            if not saved_path:
                continue

            image = ProductImage(
                image_path=saved_path,
                is_main=(saved_count == 0),
                sort_order=index,
                product_id=product.id
            )
            db.session.add(image)
            saved_count += 1

        db.session.commit()

        flash("Product created successfully.", "success")
        return redirect(url_for("main.admin_dashboard"))

    return render_template("admin/create_product.html")


@main.route("/admin/products/<int:product_id>/edit")
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("admin/edit_product.html", product=product)


@main.route("/admin/products/<int:product_id>/update", methods=["POST"])
def update_product(product_id):
    product = Product.query.get_or_404(product_id)

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    price_raw = request.form.get("price", "").strip()
    main_image_id = request.form.get("main_image_id")

    if not title:
        flash("Product title is required.", "error")
        return redirect(url_for("main.edit_product", product_id=product.id))

    price = None
    if price_raw:
        try:
            price = float(price_raw)
        except ValueError:
            flash("Price must be a valid number.", "error")
            return redirect(url_for("main.edit_product", product_id=product.id))

    product.title = title
    product.description = description
    product.price = price

    if main_image_id:
        for image in product.images:
            image.is_main = str(image.id) == str(main_image_id)

    uploaded_files = request.files.getlist("images")
    next_image_sort = len(product.images) + 1

    for file in uploaded_files:
        saved_path = save_uploaded_file(file, current_app.config["UPLOAD_FOLDER"])
        if not saved_path:
            continue

        image = ProductImage(
            image_path=saved_path,
            is_main=False if product.images else True,
            sort_order=next_image_sort,
            product_id=product.id
        )
        db.session.add(image)
        next_image_sort += 1

    db.session.commit()
    flash("Product updated successfully.", "success")
    return redirect(url_for("main.edit_product", product_id=product.id))


@main.route("/admin/products/<int:product_id>/delete", methods=["POST"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    for image in product.images:
        delete_uploaded_file(image.image_path, current_app.static_folder)

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully.", "success")
    return redirect(url_for("main.admin_dashboard"))


@main.route("/admin/products/<int:product_id>/images/<int:image_id>/delete", methods=["POST"])
def delete_product_image(product_id, image_id):
    product = Product.query.get_or_404(product_id)
    image = ProductImage.query.filter_by(id=image_id, product_id=product.id).first_or_404()

    was_main = image.is_main
    delete_uploaded_file(image.image_path, current_app.static_folder)
    db.session.delete(image)
    db.session.commit()

    remaining_images = ProductImage.query.filter_by(product_id=product.id).order_by(ProductImage.sort_order.asc()).all()
    if remaining_images and was_main:
        remaining_images[0].is_main = True
        db.session.commit()

    flash("Product image deleted successfully.", "success")
    return redirect(url_for("main.edit_product", product_id=product.id))


@main.route("/admin/reviews")
def reviews_dashboard():
    reviews = Review.query.order_by(Review.sort_order.asc(), Review.id.asc()).all()
    return render_template("admin/reviews_dashboard.html", reviews=reviews)


@main.route("/admin/reviews/create", methods=["GET", "POST"])
def create_review():
    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        title = request.form.get("title", "").strip()
        review_text = request.form.get("review_text", "").strip()
        badge = request.form.get("badge", "").strip()
        score = request.form.get("score", "★★★★★").strip() or "★★★★★"

        if not customer_name or not title or not review_text:
            flash("Customer name, title, and review text are required.", "error")
            return redirect(url_for("main.create_review"))

        max_sort_order = db.session.query(db.func.max(Review.sort_order)).scalar()
        next_sort_order = (max_sort_order or 0) + 1

        review = Review(
            customer_name=customer_name,
            title=title,
            review_text=review_text,
            badge=badge if badge else None,
            score=score,
            sort_order=next_sort_order
        )

        db.session.add(review)
        db.session.commit()

        uploaded_files = request.files.getlist("images")
        saved_count = 0

        for index, file in enumerate(uploaded_files, start=1):
            saved_path = save_uploaded_file(file, current_app.config["UPLOAD_FOLDER"])
            if not saved_path:
                continue

            image = ReviewImage(
                image_path=saved_path,
                is_main=(saved_count == 0),
                sort_order=index,
                review_id=review.id
            )
            db.session.add(image)
            saved_count += 1

        if saved_count == 0:
            default_image = ReviewImage(
                image_path="images/review1.jpg",
                is_main=True,
                sort_order=1,
                review_id=review.id
            )
            db.session.add(default_image)

        db.session.commit()

        flash("Review created successfully.", "success")
        return redirect(url_for("main.reviews_dashboard"))

    return render_template("admin/create_review.html")


@main.route("/admin/reviews/<int:review_id>/edit", methods=["GET", "POST"])
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)

    if request.method == "POST":
        customer_name = request.form.get("customer_name", "").strip()
        title = request.form.get("title", "").strip()
        review_text = request.form.get("review_text", "").strip()
        badge = request.form.get("badge", "").strip()
        score = request.form.get("score", "★★★★★").strip() or "★★★★★"
        main_image_id = request.form.get("main_image_id")

        if not customer_name or not title or not review_text:
            flash("Customer name, title, and review text are required.", "error")
            return redirect(url_for("main.edit_review", review_id=review.id))

        review.customer_name = customer_name
        review.title = title
        review.review_text = review_text
        review.badge = badge if badge else None
        review.score = score

        if main_image_id:
            for image in review.images:
                image.is_main = str(image.id) == str(main_image_id)

        uploaded_files = request.files.getlist("images")
        next_image_sort = len(review.images) + 1

        for file in uploaded_files:
            saved_path = save_uploaded_file(file, current_app.config["UPLOAD_FOLDER"])
            if not saved_path:
                continue

            image = ReviewImage(
                image_path=saved_path,
                is_main=False if review.images else True,
                sort_order=next_image_sort,
                review_id=review.id
            )
            db.session.add(image)
            next_image_sort += 1

        db.session.commit()

        flash("Review updated successfully.", "success")
        return redirect(url_for("main.reviews_dashboard"))

    return render_template("admin/edit_review.html", review=review)


@main.route("/admin/reviews/<int:review_id>/delete", methods=["POST"])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    for image in review.images:
        delete_uploaded_file(image.image_path, current_app.static_folder)

    db.session.delete(review)
    db.session.commit()

    flash("Review deleted successfully.", "success")
    return redirect(url_for("main.reviews_dashboard"))


@main.route("/admin/reviews/<int:review_id>/images/<int:image_id>/delete", methods=["POST"])
def delete_review_image(review_id, image_id):
    review = Review.query.get_or_404(review_id)
    image = ReviewImage.query.filter_by(id=image_id, review_id=review.id).first_or_404()

    was_main = image.is_main
    delete_uploaded_file(image.image_path, current_app.static_folder)
    db.session.delete(image)
    db.session.commit()

    remaining_images = ReviewImage.query.filter_by(review_id=review.id).order_by(ReviewImage.sort_order.asc()).all()
    if remaining_images and was_main:
        remaining_images[0].is_main = True
        db.session.commit()

    flash("Review image deleted successfully.", "success")
    return redirect(url_for("main.edit_review", review_id=review.id))