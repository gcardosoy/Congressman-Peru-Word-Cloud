from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Usuario',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Correo',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Ingresar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')

class LoginForm(FlaskForm):
    email = StringField('Correo',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember = BooleanField('Recuerdame')
    submit = SubmitField('Iniciar Sesión')

class OpinionForm(FlaskForm):
    congresistaUser = StringField('congresistaUser')
    inteligence = RadioField('Inteligencia', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], validators=[DataRequired()])
    trust = RadioField('Confianza', choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')], validators=[DataRequired()])
    opinion = StringField('Opinión', validators=[DataRequired()])
    submit = SubmitField('Enviar Opinión')


