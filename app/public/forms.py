from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[Optional(), Length(max=30)])
    offering_id = SelectField("Regarding", validators=[Optional()], choices=[])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=2000)])

    # Honeypot: real users never see or fill this (hidden via CSS in the template).
    # Bots that auto-fill every field will trip it. If it's non-empty, silently
    # drop the submission instead of erroring - don't tip off the bot.
    website = StringField("Website", validators=[Optional()])

    submit = SubmitField("Send Message")

    def is_spam(self) -> bool:
        return bool(self.website.data)
