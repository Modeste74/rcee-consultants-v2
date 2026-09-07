from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional

from app.utils.images import ALLOWED_EXTENSIONS

_image_validators = [Optional(), FileAllowed(list(ALLOWED_EXTENSIONS), "Images only (jpg, png, webp).")]


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")


class OfferingForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=150)])
    type = SelectField("Type", choices=[("program", "Program"), ("service", "Service")], validators=[DataRequired()])
    description = TextAreaField("Description", validators=[DataRequired()])
    image = FileField("Image", validators=_image_validators)
    is_published = BooleanField("Published", default=True)
    submit = SubmitField("Save")


class TestimonialForm(FlaskForm):
    author_name = StringField("Author Name", validators=[DataRequired(), Length(max=120)])
    quote = TextAreaField("Quote", validators=[DataRequired()])
    offering_id = SelectField("Related Offering", validators=[Optional()], choices=[])
    is_published = BooleanField("Published", default=True)
    submit = SubmitField("Save")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    content = TextAreaField("Content", validators=[DataRequired()])
    image = FileField("Image", validators=_image_validators)
    is_published = BooleanField("Published", default=True)
    submit = SubmitField("Save")


class HeroSectionForm(FlaskForm):
    heading = StringField("Heading", validators=[DataRequired(), Length(max=200)])
    subheading = StringField("Subheading", validators=[Optional(), Length(max=300)])
    image = FileField("Image", validators=_image_validators)
    submit = SubmitField("Save")


class AboutUsForm(FlaskForm):
    content = TextAreaField("Content", validators=[DataRequired()])
    image = FileField("Image", validators=_image_validators)
    submit = SubmitField("Save")


class OpeningStatementForm(FlaskForm):
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Save")


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Reset Link")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm New Password", validators=[DataRequired()])
    submit = SubmitField("Reset Password")
