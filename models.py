from flask_wtf import FlaskForm, RecaptchaField
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from datetime import datetime
from init import db, redis_client


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    telegram_id = db.Column(db.String(100), nullable=True)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class LoginForm(FlaskForm):
    login = StringField('Логин:', validators=[Length(min=3, max=25, message="Логин должен быть от 4 до 25 символов")])
    password = PasswordField("Пароль:", validators=[DataRequired(), Length(min=4, max=100, message="Неверный пароль")])
    remember = BooleanField("Запомнить", default=False)
    recaptcha = RecaptchaField()
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=5)])
    confirm_password = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    name = StringField('Имя', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telegram_id = StringField('Telegram_id', validators=[DataRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Зарегистрироваться')

    def validate_login(self, login):
        user = User.query.filter_by(login=login.data).first()
        if user:
            raise ValidationError('Такой логин уже существует. Пожалуйста, выберите другой.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Такой e-mail адрес уже существует. Пожалуйста, выберите другой.')


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1023), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())


class MessageService:
    def __init__(self, redis_client, cache, cache_key="chat_messages"):
        self.redis_client = redis_client
        self.cache = cache
        self.cache_key = cache_key

    def format_messages(self, messages, current_user):
        formatted_messages = []
        for message in messages:
            user_info = db.session.query(User).get(message.user_id)
            formatted_message = {
                'message': message.text,
                'user_id': message.user_id,
                'created_at': message.created_at.strftime('%H:%M'),
                'user_name': user_info.login,
                'is_current_user': (message.user_id == current_user.id)  # Логика с current_user передается через аргумент
            }
            formatted_messages.append(formatted_message)
        return formatted_messages

    def get_messages_from_db(self, current_user):
        messages = Message.query.order_by(Message.created_at).limit(100).all()
        return self.format_messages(messages, current_user)

    def cache_messages(self, messages):
        self.cache.set(self.cache_key, messages)

    def get_cached_messages(self):
        cached_messages = self.cache.get(self.cache_key)
        return cached_messages


class OnlineStatus:
    def __init__(self):
        self.online_users_key = 'online_users'

    def set_user_online(self, user_id):
        redis_client.sadd(self.online_users_key, user_id)

    def set_user_offline(self, user_id):
        redis_client.srem(self.online_users_key, user_id)

    def is_user_online(self, user_id):
        return redis_client.sismember(self.online_users_key, user_id)

