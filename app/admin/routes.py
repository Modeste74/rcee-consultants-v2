import os

from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from app.extensions import db, login_manager
from app.models import (
    Admin, Offering, OfferingType, Testimonial, Post, Inquiry, InquiryStatus,
    HeroSection, AboutUs, OpeningStatement,
)
from app.admin.forms import (
    LoginForm, ForgotPasswordForm, ResetPasswordForm,
    OfferingForm, TestimonialForm, PostForm,
    HeroSectionForm, AboutUsForm, OpeningStatementForm,
)
from app.utils.email import send_password_reset_email
from app.utils.images import process_image, save_locally
from app.utils.text import slugify, unique_slug

admin_bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="../templates/admin")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Admin, user_id)


def _get_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.check_password(form.password.data):
            login_user(admin)
            return redirect(url_for("admin.dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("admin/login.html", form=form)


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


def _handle_image_upload(file_storage):
    """Process + store an uploaded image, returning its URL, or None if no
    file was submitted. Local-disk storage is a dev-only fallback - swap
    this for a Cloudinary upload before deploying (see app/utils/images.py)."""
    if not file_storage or not file_storage.filename:
        return None
    image_bytes, filename = process_image(
        file_storage,
        max_dimension=current_app.config["MAX_IMAGE_DIMENSION"],
        quality=current_app.config["IMAGE_QUALITY"],
    )
    upload_dir = os.path.join(current_app.root_path, "static", "uploads")
    return save_locally(image_bytes, filename, upload_dir)


@admin_bp.route("/")
@login_required
def dashboard():
    counts = {
        "offerings": Offering.query.count(),
        "testimonials": Testimonial.query.count(),
        "posts": Post.query.count(),
        "new_inquiries": Inquiry.query.filter_by(status=InquiryStatus.NEW).count(),
    }
    return render_template("admin/dashboard.html", counts=counts)


# ---------------------------------------------------------------------------
# Offerings
# ---------------------------------------------------------------------------

@admin_bp.route("/offerings")
@login_required
def offerings_list():
    items = Offering.query.order_by(Offering.name).all()
    return render_template("admin/offerings_list.html", offerings=items)


@admin_bp.route("/offerings/new", methods=["GET", "POST"])
@login_required
def offering_new():
    form = OfferingForm()
    if form.validate_on_submit():
        offering = Offering(
            name=form.name.data,
            slug=unique_slug(slugify(form.name.data), Offering),
            type=OfferingType(form.type.data),
            description=form.description.data,
            is_published=form.is_published.data,
        )
        image_url = _handle_image_upload(form.image.data)
        if image_url:
            offering.image_url = image_url
        db.session.add(offering)
        db.session.commit()
        flash("Offering created.", "success")
        return redirect(url_for("admin.offerings_list"))
    return render_template("admin/offering_form.html", form=form, offering=None)


@admin_bp.route("/offerings/<offering_id>/edit", methods=["GET", "POST"])
@login_required
def offering_edit(offering_id):
    offering = db.get_or_404(Offering, offering_id)
    form = OfferingForm(obj=offering)
    if request.method == "GET":
        form.type.data = offering.type.value
    if form.validate_on_submit():
        offering.name = form.name.data
        offering.slug = unique_slug(slugify(form.name.data), Offering, exclude_id=offering.id)
        offering.type = OfferingType(form.type.data)
        offering.description = form.description.data
        offering.is_published = form.is_published.data
        image_url = _handle_image_upload(form.image.data)
        if image_url:
            offering.image_url = image_url
        db.session.commit()
        flash("Offering updated.", "success")
        return redirect(url_for("admin.offerings_list"))
    return render_template("admin/offering_form.html", form=form, offering=offering)


@admin_bp.route("/offerings/<offering_id>/delete", methods=["POST"])
@login_required
def offering_delete(offering_id):
    offering = db.get_or_404(Offering, offering_id)
    db.session.delete(offering)
    db.session.commit()
    flash("Offering deleted.", "success")
    return redirect(url_for("admin.offerings_list"))


# ---------------------------------------------------------------------------
# Testimonials
# ---------------------------------------------------------------------------

@admin_bp.route("/testimonials")
@login_required
def testimonials_list():
    items = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template("admin/testimonials_list.html", testimonials=items)


def _offering_choices():
    return [("", "None")] + [(o.id, o.name) for o in Offering.query.order_by(Offering.name).all()]


@admin_bp.route("/testimonials/new", methods=["GET", "POST"])
@login_required
def testimonial_new():
    form = TestimonialForm()
    form.offering_id.choices = _offering_choices()
    if form.validate_on_submit():
        testimonial = Testimonial(
            author_name=form.author_name.data,
            quote=form.quote.data,
            offering_id=form.offering_id.data or None,
            is_published=form.is_published.data,
        )
        db.session.add(testimonial)
        db.session.commit()
        flash("Testimonial created.", "success")
        return redirect(url_for("admin.testimonials_list"))
    return render_template("admin/testimonial_form.html", form=form, testimonial=None)


@admin_bp.route("/testimonials/<testimonial_id>/edit", methods=["GET", "POST"])
@login_required
def testimonial_edit(testimonial_id):
    testimonial = db.get_or_404(Testimonial, testimonial_id)
    form = TestimonialForm(obj=testimonial)
    form.offering_id.choices = _offering_choices()
    if request.method == "GET":
        form.offering_id.data = testimonial.offering_id or ""
    if form.validate_on_submit():
        testimonial.author_name = form.author_name.data
        testimonial.quote = form.quote.data
        testimonial.offering_id = form.offering_id.data or None
        testimonial.is_published = form.is_published.data
        db.session.commit()
        flash("Testimonial updated.", "success")
        return redirect(url_for("admin.testimonials_list"))
    return render_template("admin/testimonial_form.html", form=form, testimonial=testimonial)


@admin_bp.route("/testimonials/<testimonial_id>/delete", methods=["POST"])
@login_required
def testimonial_delete(testimonial_id):
    testimonial = db.get_or_404(Testimonial, testimonial_id)
    db.session.delete(testimonial)
    db.session.commit()
    flash("Testimonial deleted.", "success")
    return redirect(url_for("admin.testimonials_list"))


# ---------------------------------------------------------------------------
# Posts
# ---------------------------------------------------------------------------

@admin_bp.route("/posts")
@login_required
def posts_list():
    items = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("admin/posts_list.html", posts=items)


@admin_bp.route("/posts/new", methods=["GET", "POST"])
@login_required
def post_new():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            slug=unique_slug(slugify(form.title.data), Post),
            content=form.content.data,
            is_published=form.is_published.data,
            author_id=current_user.id,
        )
        image_url = _handle_image_upload(form.image.data)
        if image_url:
            post.image_url = image_url
        db.session.add(post)
        db.session.commit()
        flash("Post created.", "success")
        return redirect(url_for("admin.posts_list"))
    return render_template("admin/post_form.html", form=form, post=None)


@admin_bp.route("/posts/<post_id>/edit", methods=["GET", "POST"])
@login_required
def post_edit(post_id):
    post = db.get_or_404(Post, post_id)
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = unique_slug(slugify(form.title.data), Post, exclude_id=post.id)
        post.content = form.content.data
        post.is_published = form.is_published.data
        image_url = _handle_image_upload(form.image.data)
        if image_url:
            post.image_url = image_url
        db.session.commit()
        flash("Post updated.", "success")
        return redirect(url_for("admin.posts_list"))
    return render_template("admin/post_form.html", form=form, post=post)


@admin_bp.route("/posts/<post_id>/delete", methods=["POST"])
@login_required
def post_delete(post_id):
    post = db.get_or_404(Post, post_id)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "success")
    return redirect(url_for("admin.posts_list"))


# ---------------------------------------------------------------------------
# Site content (hero / about us / opening statement) - singleton-style rows
# ---------------------------------------------------------------------------

@admin_bp.route("/content/hero", methods=["GET", "POST"])
@login_required
def content_hero():
    hero = HeroSection.query.order_by(HeroSection.updated_at.desc()).first()
    form = HeroSectionForm(obj=hero)
    if form.validate_on_submit():
        if hero is None:
            hero = HeroSection()
            db.session.add(hero)
        hero.heading = form.heading.data
        hero.subheading = form.subheading.data
        image_url = _handle_image_upload(form.image.data)
        if image_url:
            hero.image_url = image_url
        db.session.commit()
        flash("Hero section updated.", "success")
        return redirect(url_for("admin.content_hero"))
    return render_template("admin/content_hero.html", form=form, hero=hero)


@admin_bp.route("/content/about", methods=["GET", "POST"])
@login_required
def content_about():
    about = AboutUs.query.order_by(AboutUs.updated_at.desc()).first()
    form = AboutUsForm(obj=about)
    if form.validate_on_submit():
        if about is None:
            about = AboutUs()
            db.session.add(about)
        about.content = form.content.data
        image_url = _handle_image_upload(form.image.data)
        if image_url:
            about.image_url = image_url
        db.session.commit()
        flash("About Us updated.", "success")
        return redirect(url_for("admin.content_about"))
    return render_template("admin/content_about.html", form=form, about=about)


@admin_bp.route("/content/opening", methods=["GET", "POST"])
@login_required
def content_opening():
    opening = OpeningStatement.query.order_by(OpeningStatement.updated_at.desc()).first()
    form = OpeningStatementForm(obj=opening)
    if form.validate_on_submit():
        if opening is None:
            opening = OpeningStatement()
            db.session.add(opening)
        opening.content = form.content.data
        db.session.commit()
        flash("Opening statement updated.", "success")
        return redirect(url_for("admin.content_opening"))
    return render_template("admin/content_opening.html", form=form, opening=opening)


# ---------------------------------------------------------------------------
# Inquiries (leads)
# ---------------------------------------------------------------------------

@admin_bp.route("/inquiries")
@login_required
def inquiries_list():
    items = Inquiry.query.order_by(Inquiry.created_at.desc()).all()
    return render_template("admin/inquiries_list.html", inquiries=items)


@admin_bp.route("/inquiries/<inquiry_id>/status", methods=["POST"])
@login_required
def inquiry_update_status(inquiry_id):
    inquiry = db.get_or_404(Inquiry, inquiry_id)
    new_status = request.form.get("status")
    if new_status in InquiryStatus._value2member_map_:
        inquiry.status = InquiryStatus(new_status)
        db.session.commit()
        flash("Inquiry status updated.", "success")
    return redirect(url_for("admin.inquiries_list"))


@admin_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        # Always show the same message whether or not the email exists -
        # avoids leaking which emails are registered admins.
        if admin:
            token = _get_serializer().dumps(admin.id, salt="password-reset")
            reset_url = url_for("admin.reset_password", token=token, _external=True)
            try:
                send_password_reset_email(admin, reset_url)
            except Exception:
                current_app.logger.exception("Failed to send password reset email")
        flash("If that email is registered, a reset link has been sent.", "info")
        return redirect(url_for("admin.login"))
    return render_template("admin/forgot_password.html", form=form)


@admin_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        admin_id = _get_serializer().loads(
            token, salt="password-reset", max_age=current_app.config["RESET_TOKEN_MAX_AGE"]
        )
    except SignatureExpired:
        flash("That reset link has expired. Please request a new one.", "error")
        return redirect(url_for("admin.forgot_password"))
    except BadSignature:
        flash("Invalid reset link.", "error")
        return redirect(url_for("admin.forgot_password"))

    admin = db.session.get(Admin, admin_id)
    if not admin:
        flash("Invalid reset link.", "error")
        return redirect(url_for("admin.forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        if form.password.data != form.confirm_password.data:
            flash("Passwords do not match.", "error")
        else:
            admin.set_password(form.password.data)
            db.session.commit()
            flash("Password updated. You can now log in.", "success")
            return redirect(url_for("admin.login"))
    return render_template("admin/reset_password.html", form=form)
