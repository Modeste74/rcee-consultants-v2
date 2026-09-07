from flask import Blueprint, render_template, redirect, url_for, flash, current_app

from app.extensions import db
from app.models import Offering, Testimonial, Post, HeroSection, AboutUs, OpeningStatement, Inquiry
from app.public.forms import ContactForm
from app.utils.email import send_inquiry_notification

public_bp = Blueprint("public", __name__, template_folder="../templates/public")


@public_bp.route("/")
def home():
    hero = HeroSection.query.order_by(HeroSection.updated_at.desc()).first()
    opening_statement = OpeningStatement.query.order_by(OpeningStatement.updated_at.desc()).first()
    testimonials = Testimonial.query.filter_by(is_published=True).limit(6).all()
    featured_offerings = Offering.query.filter_by(is_published=True).limit(3).all()
    return render_template(
        "public/home.html",
        hero=hero,
        opening_statement=opening_statement,
        testimonials=testimonials,
        offerings=featured_offerings,
    )


@public_bp.route("/about")
def about():
    about_us = AboutUs.query.order_by(AboutUs.updated_at.desc()).first()
    return render_template("public/about.html", about_us=about_us)


@public_bp.route("/offerings")
def offerings():
    items = Offering.query.filter_by(is_published=True).order_by(Offering.name).all()
    return render_template("public/offerings.html", offerings=items)


@public_bp.route("/offerings/<slug>")
def offering_detail(slug):
    offering = Offering.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template("public/offering_detail.html", offering=offering)


@public_bp.route("/blog")
def blog():
    posts = Post.query.filter_by(is_published=True).order_by(Post.created_at.desc()).all()
    return render_template("public/blog.html", posts=posts)


@public_bp.route("/blog/<slug>")
def post_detail(slug):
    post = Post.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template("public/post_detail.html", post=post)


@public_bp.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()
    form.offering_id.choices = [("", "General inquiry")] + [
        (o.id, o.name) for o in Offering.query.filter_by(is_published=True).all()
    ]

    if form.validate_on_submit():
        if form.is_spam():
            # Pretend it worked - don't reveal the honeypot to the bot.
            return redirect(url_for("public.contact", sent=1))

        inquiry = Inquiry(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            offering_id=form.offering_id.data or None,
            message=form.message.data,
        )
        db.session.add(inquiry)
        db.session.commit()

        try:
            send_inquiry_notification(inquiry)
        except Exception:
            current_app.logger.exception("Failed to send inquiry notification email")

        flash("Thanks for reaching out! We'll be in touch soon.", "success")
        return redirect(url_for("public.contact"))

    return render_template("public/contact.html", form=form)


@public_bp.route("/privacy")
def privacy():
    return render_template("public/privacy.html")
